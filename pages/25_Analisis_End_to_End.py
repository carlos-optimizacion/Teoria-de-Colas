import streamlit as st
import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

st.set_page_config(
    page_title="Modo Analista | Dimensionamiento de Operadores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Estilo ejecutivo
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background: #F6F8FB; }
    .block-container { padding-top: 1.1rem; padding-bottom: 2.3rem; max-width: 1450px; }
    .hero {
        background: linear-gradient(135deg, #163A5F 0%, #1F4E78 62%, #2D6A9F 100%);
        border-radius: 22px;
        padding: 28px 32px;
        color: white;
        box-shadow: 0 12px 28px rgba(23, 50, 77, 0.16);
        margin-bottom: 1rem;
    }
    .hero h1 { margin: 0; font-size: 2.1rem; line-height: 1.15; }
    .hero p { margin: .6rem 0 0; opacity: .93; max-width: 1050px; font-size: 1.02rem; }
    .eyebrow { font-size: .76rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; opacity: .82; }
    .decision-card {
        background: #FFFFFF;
        border: 1px solid #DDE5EC;
        border-left: 6px solid #1F4E78;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 6px 18px rgba(31, 78, 120, 0.06);
        margin: .35rem 0 1rem;
    }
    .decision-card h3 { margin: 0 0 .35rem; color: #17324D; }
    .decision-card p { margin: .25rem 0; color: #4B5563; }
    .alert-card {
        background: #FFF7E6;
        border: 1px solid #F1D6A8;
        border-left: 6px solid #D97706;
        border-radius: 14px;
        padding: 15px 18px;
        margin: .4rem 0 1rem;
        color: #7C4A03;
    }
    .critical-card {
        background: #FDECEC;
        border: 1px solid #F3C6C6;
        border-left: 6px solid #B42318;
        border-radius: 14px;
        padding: 15px 18px;
        margin: .4rem 0 1rem;
        color: #8A1C15;
    }
    .ok-card {
        background: #EAF7EF;
        border: 1px solid #CBE8D5;
        border-left: 6px solid #15803D;
        border-radius: 14px;
        padding: 15px 18px;
        margin: .4rem 0 1rem;
        color: #14532D;
    }
    .small-note { color: #667085; font-size: .88rem; }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E1E7EE;
        padding: 14px 16px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(31, 78, 120, 0.04);
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #E1E7EE;
        border-radius: 12px;
        overflow: hidden;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Motor M/M/s - Erlang C
# -----------------------------------------------------------------------------
def calcular_mms(t_llegada_min, t_atencion_min, servidores):
    lam = 60.0 / t_llegada_min
    mu = 60.0 / t_atencion_min
    rho = lam / (servidores * mu)

    if rho >= 1:
        return {
            "estable": False,
            "lambda": lam,
            "mu": mu,
            "rho": rho,
            "P_espera": 1.0,
            "Lq": float("inf"),
            "Wq": float("inf"),
            "W": float("inf"),
        }

    a = lam / mu
    termino = 1.0
    suma = 1.0

    for n in range(1, servidores):
        termino *= a / n
        suma += termino

    termino_s = termino * a / servidores
    erlang_c_term = termino_s / (1 - rho)
    p0 = 1.0 / (suma + erlang_c_term)
    p_espera = erlang_c_term * p0

    lq = p_espera * rho / (1 - rho)
    wq = lq / lam
    w = wq + 1 / mu

    return {
        "estable": True,
        "lambda": lam,
        "mu": mu,
        "rho": rho,
        "P_espera": p_espera,
        "Lq": lq,
        "Wq": wq,
        "W": w,
    }


def costos(resultado, servidores, costo_operador_h, costo_espera_cliente_h):
    costo_personal = servidores * costo_operador_h
    if not resultado["estable"] or not math.isfinite(resultado["Lq"]):
        return {
            "personal": costo_personal,
            "espera": float("inf"),
            "total": float("inf"),
        }
    costo_espera = resultado["Lq"] * costo_espera_cliente_h
    return {
        "personal": costo_personal,
        "espera": costo_espera,
        "total": costo_personal + costo_espera,
    }


def texto_pdf(valor):
    return str(valor).encode("latin-1", "ignore").decode("latin-1")


def generar_pdf(nombre, datos, actual, recomendado, economia):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, texto_pdf("Resumen Ejecutivo - Dimensionamiento de Operadores"), ln=True, align="C")
    pdf.ln(3)

    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, texto_pdf(
        f"Proceso: {nombre}\n"
        f"Llegada promedio: 1 cliente cada {datos['t_llegada']:.2f} min\n"
        f"Tiempo promedio de atencion: {datos['t_atencion']:.2f} min/cliente\n"
        f"Operadores actuales: {datos['operadores_actuales']}\n"
        f"Meta de espera: {datos['meta_wq']:.2f} min"
    ))

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, texto_pdf("Situacion actual"), ln=True)
    pdf.set_font("Arial", "", 10)
    if actual["estable"]:
        pdf.multi_cell(0, 6, texto_pdf(
            f"Utilizacion: {actual['rho']*100:.1f}%\n"
            f"Probabilidad de esperar: {actual['P_espera']*100:.1f}%\n"
            f"Clientes promedio en cola: {actual['Lq']:.2f}\n"
            f"Espera promedio: {actual['Wq']*60:.2f} min"
        ))
    else:
        pdf.multi_cell(0, 6, texto_pdf(
            "La configuracion actual es inestable: la capacidad agregada de atencion es insuficiente para absorber la demanda."
        ))

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, texto_pdf("Configuracion recomendada"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, texto_pdf(
        f"Operadores recomendados: {int(recomendado['Operadores'])}\n"
        f"Utilizacion: {recomendado['Utilizacion %']:.1f}%\n"
        f"Probabilidad de esperar: {recomendado['Prob. espera %']:.1f}%\n"
        f"Espera promedio: {recomendado['Espera promedio (min)']:.2f} min\n"
        f"Costo total estimado: S/ {recomendado['Costo total (S//h)']:.2f}/h"
    ))

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, texto_pdf("Costo-beneficio"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, texto_pdf(
        f"Costo adicional de operadores: S/ {economia['costo_adicional_personal']:+.2f}/h\n"
        f"Ahorro por menor espera: S/ {economia['ahorro_espera']:+.2f}/h\n"
        f"Beneficio neto estimado: S/ {economia['beneficio_neto']:+.2f}/h"
    ))

    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5, texto_pdf(
        "Nota: el analisis supone llegadas Poisson, tiempos de servicio exponenciales, una sola cola y operadores equivalentes. "
        "Los costos deben parametrizarse con informacion real antes de tomar una decision de implementacion."
    ))

    return bytes(pdf.output(dest="S").encode("latin-1"))


# -----------------------------------------------------------------------------
# Encabezado
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Modo Analista · Dimensionamiento de Capacidad</div>
        <h1>¿Cuántos operadores necesita el proceso?</h1>
        <p>
            Ingresa los tiempos reales de llegada y atención. La herramienta compara la dotación actual
            con distintas cantidades de operadores y encuentra una alternativa que equilibre servicio al cliente y costo.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Entradas simples
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Datos de la operación")
    st.caption("Solo se solicitan los datos necesarios para dimensionar la atención.")

    with st.form("analisis_operadores"):
        nombre = st.text_input("Proceso / servicio", value="Atención al cliente")

        st.markdown("### Flujo de clientes")
        t_llegada = st.number_input(
            "Llega 1 cliente cada... (min)",
            min_value=0.1,
            value=4.0,
            step=0.5,
            help="Tiempo promedio entre una llegada y la siguiente."
        )
        t_atencion = st.number_input(
            "Cada atención demora... (min)",
            min_value=0.1,
            value=7.0,
            step=0.5,
            help="Tiempo promedio que un operador dedica a un cliente."
        )

        st.markdown("### Dotación")
        operadores_actuales = st.number_input(
            "Operadores actuales",
            min_value=1,
            max_value=100,
            value=2,
            step=1,
        )
        max_operadores = st.number_input(
            "Evaluar hasta... operadores",
            min_value=1,
            max_value=100,
            value=10,
            step=1,
        )

        st.markdown("### Servicio al cliente")
        meta_wq = st.number_input(
            "Meta máxima de espera (min)",
            min_value=0.0,
            value=10.0,
            step=1.0,
            help="Tiempo promedio máximo que la organización considera aceptable para el cliente."
        )

        st.markdown("### Costo-beneficio")
        costo_operador = st.number_input(
            "Costo por operador (S/ por hora)",
            min_value=0.0,
            value=20.0,
            step=1.0,
        )
        costo_espera = st.number_input(
            "Costo de espera (S/ por cliente-hora)",
            min_value=0.0,
            value=12.0,
            step=1.0,
            help="Valor económico estimado de mantener a un cliente esperando durante una hora."
        )

        ejecutar = st.form_submit_button("Analizar dotación", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# Cálculo y persistencia
# -----------------------------------------------------------------------------
if ejecutar:
    if int(max_operadores) < int(operadores_actuales):
        st.sidebar.error("El máximo de operadores a evaluar debe ser igual o mayor a la dotación actual.")
    else:
        actual = calcular_mms(t_llegada, t_atencion, int(operadores_actuales))
        escenarios = []

        for s in range(1, int(max_operadores) + 1):
            r = calcular_mms(t_llegada, t_atencion, s)
            c = costos(r, s, costo_operador, costo_espera)
            escenarios.append({
                "Operadores": s,
                "Estable": r["estable"],
                "Utilizacion %": round(r["rho"] * 100, 1),
                "Prob. espera %": round(r["P_espera"] * 100, 1),
                "Clientes en cola": round(r["Lq"], 2) if math.isfinite(r["Lq"]) else float("inf"),
                "Espera promedio (min)": round(r["Wq"] * 60, 2) if math.isfinite(r["Wq"]) else float("inf"),
                "Costo personal (S//h)": round(c["personal"], 2),
                "Costo espera (S//h)": round(c["espera"], 2) if math.isfinite(c["espera"]) else float("inf"),
                "Costo total (S//h)": round(c["total"], 2) if math.isfinite(c["total"]) else float("inf"),
            })

        df = pd.DataFrame(escenarios)
        candidatos = df[
            (df["Estable"] == True)
            & (df["Espera promedio (min)"] <= meta_wq)
        ].copy()

        if not candidatos.empty:
            recomendado = candidatos.sort_values(
                ["Costo total (S//h)", "Operadores"]
            ).iloc[0].to_dict()
            motivo = "cumple la meta de espera y presenta el menor costo total entre las configuraciones que cumplen el nivel de servicio."
            cumple_meta = True
        else:
            estables = df[df["Estable"] == True].copy()
            if estables.empty:
                recomendado = df.iloc[-1].to_dict()
                motivo = "no se encontró una configuración estable dentro del rango evaluado."
                cumple_meta = False
            else:
                recomendado = estables.sort_values(
                    ["Espera promedio (min)", "Costo total (S//h)"]
                ).iloc[0].to_dict()
                motivo = "ninguna configuración cumple la meta de espera; se muestra la alternativa estable con menor espera dentro del rango evaluado."
                cumple_meta = False

        costo_actual = costos(actual, int(operadores_actuales), costo_operador, costo_espera)
        costo_rec_personal = float(recomendado["Costo personal (S//h)"])
        costo_rec_espera = float(recomendado["Costo espera (S//h)"])

        if actual["estable"] and math.isfinite(costo_actual["espera"]):
            costo_adicional_personal = costo_rec_personal - costo_actual["personal"]
            ahorro_espera = costo_actual["espera"] - costo_rec_espera
            beneficio_neto = ahorro_espera - costo_adicional_personal
        else:
            costo_adicional_personal = costo_rec_personal - costo_actual["personal"]
            ahorro_espera = float("nan")
            beneficio_neto = float("nan")

        st.session_state["analisis_dotacion"] = {
            "nombre": nombre,
            "t_llegada": t_llegada,
            "t_atencion": t_atencion,
            "operadores_actuales": int(operadores_actuales),
            "max_operadores": int(max_operadores),
            "meta_wq": meta_wq,
            "costo_operador": costo_operador,
            "costo_espera": costo_espera,
            "actual": actual,
            "df": df,
            "recomendado": recomendado,
            "motivo": motivo,
            "cumple_meta": cumple_meta,
            "economia": {
                "costo_adicional_personal": costo_adicional_personal,
                "ahorro_espera": ahorro_espera,
                "beneficio_neto": beneficio_neto,
            },
        }

# -----------------------------------------------------------------------------
# Estado inicial
# -----------------------------------------------------------------------------
if "analisis_dotacion" not in st.session_state:
    st.markdown("### Qué responde esta herramienta")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**1. Situación actual**\n\n¿La dotación actual puede absorber la demanda y cuánto espera el cliente?")
    with c2:
        st.info("**2. Dotación requerida**\n\n¿Cómo cambia la espera cuando agregamos o reducimos operadores?")
    with c3:
        st.info("**3. Decisión económica**\n\n¿Cuál alternativa equilibra mejor costo de personal y costo de espera?")
    st.stop()

# -----------------------------------------------------------------------------
# Dashboard gerencial
# -----------------------------------------------------------------------------
r = st.session_state["analisis_dotacion"]
actual = r["actual"]
df = r["df"]
recomendado = r["recomendado"]

st.markdown(f"### {r['nombre']}")

# Alertas operativas
if r["t_llegada"] < r["t_atencion"]:
    if actual["rho"] >= 1:
        st.markdown(
            f"""
            <div class="critical-card">
                <b>ALERTA CRÍTICA DE CAPACIDAD</b><br>
                Llega un cliente cada <b>{r['t_llegada']:.1f} min</b>, mientras una atención requiere
                <b>{r['t_atencion']:.1f} min</b>. Además, con {r['operadores_actuales']} operador(es)
                la capacidad total actual no logra absorber la demanda. La cola tenderá a crecer mientras se mantenga este patrón.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="alert-card">
                <b>ALERTA DE PRESIÓN DE COLA</b><br>
                Los clientes llegan más rápido de lo que un operador individual puede atenderlos:
                llegada cada <b>{r['t_llegada']:.1f} min</b> vs atención de <b>{r['t_atencion']:.1f} min</b>.
                La dotación conjunta actual mantiene el sistema estable, pero existe probabilidad de espera.
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        """
        <div class="ok-card">
            <b>FLUJO INDIVIDUAL FAVORABLE</b><br>
            El tiempo promedio de atención de un operador no supera el intervalo promedio entre llegadas.
            Aun así, la variabilidad aleatoria puede generar espera y debe revisarse la utilización del sistema.
        </div>
        """,
        unsafe_allow_html=True,
    )

# Situación actual
st.markdown("### 1. Situación actual")
if actual["estable"]:
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Operadores actuales", r["operadores_actuales"])
    a2.metric("Utilización", f"{actual['rho']*100:.1f}%")
    a3.metric("Probabilidad de esperar", f"{actual['P_espera']*100:.1f}%")
    a4.metric("Espera promedio", f"{actual['Wq']*60:.2f} min")
else:
    a1, a2, a3 = st.columns(3)
    a1.metric("Operadores actuales", r["operadores_actuales"])
    a2.metric("Utilización requerida", f"{actual['rho']*100:.1f}%")
    a3.metric("Estado", "Inestable")
    st.error("La demanda supera la capacidad agregada actual. La espera teórica no tiene un valor finito mientras se mantenga esta configuración.")

# Gráfico gerencial principal
st.markdown("### 2. ¿Qué pasa si cambiamos la cantidad de operadores?")
st.caption("La línea horizontal representa la meta máxima de espera definida por la organización.")

plot_df = df[df["Estable"] == True].copy()
if not plot_df.empty:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=plot_df["Operadores"],
        y=plot_df["Espera promedio (min)"],
        name="Espera promedio",
        text=[f"{v:.1f}" for v in plot_df["Espera promedio (min)"]],
        textposition="outside",
    ))
    fig.add_hline(
        y=r["meta_wq"],
        line_dash="dash",
        annotation_text=f"Meta: {r['meta_wq']:.1f} min",
        annotation_position="top right",
    )
    fig.add_vline(
        x=float(recomendado["Operadores"]),
        line_dash="dot",
        annotation_text=f"Recomendado: {int(recomendado['Operadores'])}",
        annotation_position="top left",
    )
    fig.update_layout(
        title="Tiempo promedio de espera según cantidad de operadores",
        xaxis_title="Número de operadores",
        yaxis_title="Minutos de espera",
        template="plotly_white",
        showlegend=False,
        height=430,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Ninguna configuración estable fue encontrada dentro del rango evaluado.")

# Recomendación
st.markdown("### 3. Recomendación de dotación")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Operadores recomendados", int(recomendado["Operadores"]), delta=int(recomendado["Operadores"]) - r["operadores_actuales"])
r2.metric("Utilización", f"{recomendado['Utilizacion %']:.1f}%")
r3.metric("Prob. de esperar", f"{recomendado['Prob. espera %']:.1f}%")
r4.metric("Espera promedio", f"{recomendado['Espera promedio (min)']:.2f} min")

if r["cumple_meta"]:
    st.success(f"La configuración recomendada {r['motivo']}")
else:
    st.warning(r["motivo"].capitalize())

# Costo-beneficio
st.markdown("### 4. Costo-beneficio y servicio al cliente")
e = r["economia"]

if actual["estable"] and math.isfinite(e["beneficio_neto"]):
    e1, e2, e3 = st.columns(3)
    e1.metric("Costo adicional de personal", f"S/ {e['costo_adicional_personal']:+.2f}/h", delta_color="inverse")
    e2.metric("Ahorro por menor espera", f"S/ {e['ahorro_espera']:+.2f}/h")
    e3.metric("Beneficio neto estimado", f"S/ {e['beneficio_neto']:+.2f}/h")

    comp_costos = pd.DataFrame([
        {
            "Escenario": "Actual",
            "Costo total (S//h)": float(df.loc[df["Operadores"] == r["operadores_actuales"], "Costo total (S//h)"].iloc[0])
        },
        {
            "Escenario": "Recomendado",
            "Costo total (S//h)": float(recomendado["Costo total (S//h)"])
        },
    ])
    fig_cost = px.bar(
        comp_costos,
        x="Escenario",
        y="Costo total (S//h)",
        text_auto=".2f",
        title="Costo operativo total por hora: situación actual vs recomendada",
        template="plotly_white",
    )
    fig_cost.update_layout(yaxis_title="S/ por hora", xaxis_title="")
    st.plotly_chart(fig_cost, use_container_width=True)
else:
    st.warning(
        "La situación actual es inestable, por lo que el costo de espera teórico no es finito y no puede compararse económicamente de forma directa. "
        "Sí se muestra el costo de la configuración recomendada una vez que el sistema alcanza estabilidad."
    )

st.markdown(
    f"""
    <div class="decision-card">
        <h3>Decisión sugerida</h3>
        <p>Evaluar una dotación de <b>{int(recomendado['Operadores'])} operador(es)</b>.</p>
        <p>Con esta configuración, la espera promedio estimada es de <b>{recomendado['Espera promedio (min)']:.2f} min</b>
        y la probabilidad de que un cliente tenga que esperar es de <b>{recomendado['Prob. espera %']:.1f}%</b>.</p>
        <p>El costo total estimado es de <b>S/ {recomendado['Costo total (S//h)']:.2f} por hora</b>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Detalle técnico secundario
with st.expander("Ver detalle de todas las alternativas"):
    vista = df.copy()
    vista["Cumple meta"] = (vista["Estable"] == True) & (vista["Espera promedio (min)"] <= r["meta_wq"])
    st.dataframe(vista, use_container_width=True, hide_index=True)

with st.expander("Supuestos del modelo"):
    st.markdown(
        """
        - Se utiliza un modelo M/M/s: llegadas Poisson, tiempos de atención exponenciales y operadores equivalentes.
        - Se supone una sola línea de espera y capacidad suficiente para mantener a los clientes en cola.
        - El tiempo promedio entre llegadas y el tiempo promedio de atención deben provenir de datos observados o estimaciones razonables.
        - El costo de espera representa un valor económico de la demora y debe ser definido por la organización.
        - La recomendación es un apoyo a la decisión y debe validarse con restricciones de turnos, descansos, habilidades y variabilidad real del proceso.
        """
    )

# Reporte
with st.expander("Descargar resumen ejecutivo"):
    datos_pdf = {
        "t_llegada": r["t_llegada"],
        "t_atencion": r["t_atencion"],
        "operadores_actuales": r["operadores_actuales"],
        "meta_wq": r["meta_wq"],
    }
    pdf_bytes = generar_pdf(
        r["nombre"],
        datos_pdf,
        actual,
        recomendado,
        e,
    )
    st.download_button(
        "Descargar resumen ejecutivo en PDF",
        data=pdf_bytes,
        file_name="resumen_dimensionamiento_operadores.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar alternativas en CSV",
        data=csv_bytes,
        file_name="alternativas_operadores.csv",
        mime="text/csv",
        use_container_width=True,
    )
