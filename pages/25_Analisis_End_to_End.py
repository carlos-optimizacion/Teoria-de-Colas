import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF

from queue_core import economic_cost, mms_from_minutes, recommend_mms_capacity

st.set_page_config(
    page_title="Modo Analista | Dimensionamiento de Operadores",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #F6F8FB; }
    .block-container { padding-top: 1.1rem; padding-bottom: 2.3rem; max-width: 1450px; }
    .hero { background: linear-gradient(135deg,#163A5F 0%,#1F4E78 62%,#2D6A9F 100%); border-radius:22px; padding:28px 32px; color:white; box-shadow:0 12px 28px rgba(23,50,77,.16); margin-bottom:1rem; }
    .hero h1 { margin:0; font-size:2.1rem; line-height:1.15; }
    .hero p { margin:.6rem 0 0; opacity:.93; max-width:1050px; font-size:1.02rem; }
    .eyebrow { font-size:.76rem; font-weight:700; letter-spacing:.11em; text-transform:uppercase; opacity:.82; }
    .decision-card { background:#fff; border:1px solid #DDE5EC; border-left:6px solid #1F4E78; border-radius:16px; padding:18px 20px; box-shadow:0 6px 18px rgba(31,78,120,.06); margin:.35rem 0 1rem; }
    .decision-card h3 { margin:0 0 .35rem; color:#17324D; }
    .decision-card p { margin:.25rem 0; color:#4B5563; }
    .alert-card { background:#FFF7E6; border:1px solid #F1D6A8; border-left:6px solid #D97706; border-radius:14px; padding:15px 18px; margin:.4rem 0 1rem; color:#7C4A03; }
    .critical-card { background:#FDECEC; border:1px solid #F3C6C6; border-left:6px solid #B42318; border-radius:14px; padding:15px 18px; margin:.4rem 0 1rem; color:#8A1C15; }
    .ok-card { background:#EAF7EF; border:1px solid #CBE8D5; border-left:6px solid #15803D; border-radius:14px; padding:15px 18px; margin:.4rem 0 1rem; color:#14532D; }
    div[data-testid="stMetric"] { background:#fff; border:1px solid #E1E7EE; padding:14px 16px; border-radius:14px; box-shadow:0 4px 12px rgba(31,78,120,.04); }
    #MainMenu { visibility:hidden; }
    footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


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
    pdf.multi_cell(
        0,
        6,
        texto_pdf(
            f"Proceso: {nombre}\n"
            f"Llegada promedio: 1 cliente cada {datos['t_llegada']:.2f} min\n"
            f"Tiempo promedio de atencion: {datos['t_atencion']:.2f} min/cliente\n"
            f"Operadores actuales: {datos['operadores_actuales']}\n"
            f"Meta de espera promedio: {datos['meta_wq']:.2f} min"
        ),
    )

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, texto_pdf("Situacion actual"), ln=True)
    pdf.set_font("Arial", "", 10)
    if actual["estable"]:
        pdf.multi_cell(
            0,
            6,
            texto_pdf(
                f"Utilizacion: {actual['rho'] * 100:.1f}%\n"
                f"Probabilidad de esperar: {actual['P_espera'] * 100:.1f}%\n"
                f"Clientes promedio en cola: {actual['Lq']:.2f}\n"
                f"Espera promedio: {actual['Wq'] * 60:.2f} min"
            ),
        )
    else:
        pdf.multi_cell(0, 6, texto_pdf("La configuracion actual es inestable: la demanda iguala o supera la capacidad agregada."))

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, texto_pdf("Configuracion recomendada"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0,
        6,
        texto_pdf(
            f"Operadores recomendados: {recomendado['servers']}\n"
            f"Utilizacion: {recomendado['rho'] * 100:.1f}%\n"
            f"Probabilidad de esperar: {recomendado['p_wait'] * 100:.1f}%\n"
            f"Espera promedio: {recomendado['Wq_min']:.2f} min\n"
            f"Costo total estimado: S/ {recomendado['cost_total']:.2f}/h"
        ),
    )

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, texto_pdf("Costo-beneficio"), ln=True)
    pdf.set_font("Arial", "", 10)
    if math.isfinite(economia["beneficio_neto"]):
        pdf.multi_cell(
            0,
            6,
            texto_pdf(
                f"Costo adicional de operadores: S/ {economia['costo_adicional_personal']:+.2f}/h\n"
                f"Ahorro por menor espera: S/ {economia['ahorro_espera']:+.2f}/h\n"
                f"Beneficio neto estimado: S/ {economia['beneficio_neto']:+.2f}/h"
            ),
        )
    else:
        pdf.multi_cell(0, 6, texto_pdf("No se compara el costo de espera con la situacion actual porque el sistema actual es inestable."))

    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(
        0,
        5,
        texto_pdf(
            "Supuestos: M/M/s, llegadas Poisson, servicios exponenciales, una cola comun y operadores equivalentes. "
            "Los costos y supuestos deben validarse con datos reales antes de implementar una decision."
        ),
    )
    return bytes(pdf.output(dest="S").encode("latin-1"))


st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Modo Analista · Dimensionamiento de Capacidad</div>
        <h1>¿Cuántos operadores necesita el proceso?</h1>
        <p>Ingresa datos operativos, compara escenarios de capacidad y encuentra una alternativa que cumpla la meta de servicio con el menor costo total estimado.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Datos de la operación")
    st.caption("El motor matemático es compartido con los demás módulos para evitar resultados inconsistentes.")
    with st.form("analisis_operadores"):
        nombre = st.text_input("Proceso / servicio", value="Atención al cliente")
        st.markdown("### Flujo de clientes")
        t_llegada = st.number_input("Llega 1 cliente cada... (min)", min_value=0.1, value=4.0, step=0.5)
        t_atencion = st.number_input("Cada atención demora... (min)", min_value=0.1, value=7.0, step=0.5)

        st.markdown("### Dotación")
        operadores_actuales = st.number_input("Operadores actuales", min_value=1, max_value=100, value=2, step=1)
        max_operadores = st.number_input("Evaluar hasta... operadores", min_value=1, max_value=100, value=10, step=1)

        st.markdown("### Servicio")
        meta_wq = st.number_input("Meta máxima de espera promedio (min)", min_value=0.0, value=10.0, step=1.0)

        st.markdown("### Costo-beneficio")
        costo_operador = st.number_input("Costo por operador (S/ por hora)", min_value=0.0, value=20.0, step=1.0)
        costo_espera = st.number_input("Costo de espera (S/ por cliente-hora)", min_value=0.0, value=12.0, step=1.0)
        ejecutar = st.form_submit_button("Analizar dotación", type="primary", use_container_width=True)

if ejecutar:
    if int(max_operadores) < int(operadores_actuales):
        st.sidebar.error("El máximo de operadores debe ser igual o mayor a la dotación actual.")
    else:
        actual = mms_from_minutes(t_llegada, t_atencion, int(operadores_actuales))
        escenarios, recomendado = recommend_mms_capacity(
            t_llegada_min=t_llegada,
            t_atencion_min=t_atencion,
            max_servers=int(max_operadores),
            costo_operador_h=costo_operador,
            costo_espera_cliente_h=costo_espera,
            meta_wq_min=meta_wq,
        )

        df = pd.DataFrame(
            [
                {
                    "Operadores": e["servers"],
                    "Estado": "Estable" if e["stable"] else "Inestable",
                    "Utilización %": e["rho"] * 100,
                    "Prob. espera %": e["p_wait"] * 100,
                    "Clientes en cola": e["Lq"],
                    "Espera promedio (min)": e["Wq_min"],
                    "Costo personal (S/h)": e["cost_staff"],
                    "Costo espera (S/h)": e["cost_wait"],
                    "Costo total (S/h)": e["cost_total"],
                    "Cumple meta": e["meets_service"],
                }
                for e in escenarios
            ]
        )

        costo_actual = economic_cost(actual, int(operadores_actuales), costo_operador, costo_espera)
        if actual["estable"] and math.isfinite(costo_actual["espera"]):
            costo_adicional_personal = recomendado["cost_staff"] - costo_actual["personal"]
            ahorro_espera = costo_actual["espera"] - recomendado["cost_wait"]
            beneficio_neto = ahorro_espera - costo_adicional_personal
        else:
            costo_adicional_personal = recomendado["cost_staff"] - costo_actual["personal"]
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
            "economia": {
                "costo_adicional_personal": costo_adicional_personal,
                "ahorro_espera": ahorro_espera,
                "beneficio_neto": beneficio_neto,
            },
        }

if "analisis_dotacion" not in st.session_state:
    st.markdown("### Qué responde esta herramienta")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**1. Situación actual**\n\n¿La dotación actual absorbe la demanda y cuánto espera el cliente?")
    with c2:
        st.info("**2. Dotación requerida**\n\n¿Cómo cambia la espera cuando se modifica la cantidad de operadores?")
    with c3:
        st.info("**3. Decisión económica**\n\n¿Qué alternativa cumple el servicio con menor costo total estimado?")
    st.stop()

r = st.session_state["analisis_dotacion"]
actual = r["actual"]
df = r["df"]
rec = r["recomendado"]
economia = r["economia"]

st.markdown(f"### {r['nombre']}")

if actual["rho"] >= 1:
    st.markdown(
        f'<div class="critical-card"><b>ALERTA CRÍTICA DE CAPACIDAD</b><br>Con {r["operadores_actuales"]} operador(es), la utilización requerida es {actual["rho"]*100:.1f}%. La cola no tiene estado estacionario bajo estos supuestos.</div>',
        unsafe_allow_html=True,
    )
elif actual["rho"] >= 0.85:
    st.markdown(
        f'<div class="alert-card"><b>ALTA UTILIZACIÓN</b><br>La utilización actual es {actual["rho"]*100:.1f}%. En sistemas aleatorios, trabajar cerca de la capacidad puede incrementar fuertemente la espera.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="ok-card"><b>SISTEMA ESTABLE</b><br>La configuración actual presenta una utilización de {actual["rho"]*100:.1f}% bajo el modelo M/M/s.</div>',
        unsafe_allow_html=True,
    )

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

st.markdown("### 2. Curva de espera según capacidad")
plot_df = df[df["Estado"] == "Estable"].copy()
if not plot_df.empty:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=plot_df["Operadores"],
            y=plot_df["Espera promedio (min)"],
            text=[f"{v:.1f}" for v in plot_df["Espera promedio (min)"]],
            textposition="outside",
        )
    )
    fig.add_hline(y=r["meta_wq"], line_dash="dash", annotation_text=f"Meta: {r['meta_wq']:.1f} min")
    fig.add_vline(x=rec["servers"], line_dash="dot", annotation_text=f"Seleccionado: {rec['servers']}")
    fig.update_layout(title="Tiempo de espera promedio por cantidad de operadores", xaxis_title="Operadores", yaxis_title="Minutos", template="plotly_white", showlegend=False, height=430)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No se encontró una configuración estable en el rango evaluado.")

st.markdown("### 3. Configuración seleccionada")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Operadores", rec["servers"], delta=rec["servers"] - r["operadores_actuales"])
r2.metric("Utilización", f"{rec['rho']*100:.1f}%")
r3.metric("Prob. de esperar", f"{rec['p_wait']*100:.1f}%")
r4.metric("Espera promedio", f"{rec['Wq_min']:.2f} min")

if rec["meets_service"]:
    st.success("La configuración seleccionada cumple la meta de espera y minimiza el costo total entre las alternativas que la cumplen.")
else:
    st.warning("Ninguna alternativa del rango cumple completamente la meta; se muestra la configuración estable con menor espera.")

st.markdown("### 4. Costo-beneficio")
if actual["estable"] and math.isfinite(economia["beneficio_neto"]):
    e1, e2, e3 = st.columns(3)
    e1.metric("Costo adicional de personal", f"S/ {economia['costo_adicional_personal']:+.2f}/h", delta_color="inverse")
    e2.metric("Ahorro por menor espera", f"S/ {economia['ahorro_espera']:+.2f}/h")
    e3.metric("Beneficio neto estimado", f"S/ {economia['beneficio_neto']:+.2f}/h")

    costo_actual_total = float(df.loc[df["Operadores"] == r["operadores_actuales"], "Costo total (S/h)"].iloc[0])
    comp = pd.DataFrame({"Escenario": ["Actual", "Seleccionado"], "Costo total (S/h)": [costo_actual_total, rec["cost_total"]]})
    fig_cost = px.bar(comp, x="Escenario", y="Costo total (S/h)", text_auto=".2f", title="Costo total estimado por hora", template="plotly_white")
    fig_cost.update_layout(yaxis_title="S/ por hora", xaxis_title="")
    st.plotly_chart(fig_cost, use_container_width=True)
else:
    st.warning("La situación actual es inestable; su costo teórico de espera no es finito y no se compara directamente con una configuración estable.")

st.markdown(
    f"""
    <div class="decision-card">
        <h3>Lectura ejecutiva</h3>
        <p>Evaluar <b>{rec['servers']} operador(es)</b>.</p>
        <p>Espera promedio estimada: <b>{rec['Wq_min']:.2f} min</b>; probabilidad de esperar: <b>{rec['p_wait']*100:.1f}%</b>; costo total: <b>S/ {rec['cost_total']:.2f}/h</b>.</p>
        <p>La recomendación debe contrastarse con turnos, descansos, habilidades, estacionalidad y distribución real de llegadas y servicios.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Ver todas las alternativas"):
    st.dataframe(
        df.style.format(
            {
                "Utilización %": "{:.1f}",
                "Prob. espera %": "{:.1f}",
                "Clientes en cola": "{:.2f}",
                "Espera promedio (min)": "{:.2f}",
                "Costo personal (S/h)": "S/ {:.2f}",
                "Costo espera (S/h)": "S/ {:.2f}",
                "Costo total (S/h)": "S/ {:.2f}",
            },
            na_rep="—",
        ),
        use_container_width=True,
        hide_index=True,
    )

with st.expander("Supuestos y límites"):
    st.markdown(
        """
        - Modelo M/M/s: llegadas Poisson y tiempos de servicio exponenciales.
        - Una sola cola, disciplina de atención homogénea y operadores equivalentes.
        - Los promedios de llegada y servicio deben provenir de datos observados o estimaciones justificadas.
        - La meta utilizada es de **espera promedio**; no equivale por sí sola a un SLA probabilístico.
        - El costo de espera es un parámetro de decisión y debe sustentarse con información del proceso.
        - Si las distribuciones reales no cumplen estos supuestos, debe evaluarse M/G/1 o simulación de eventos discretos.
        """
    )

with st.expander("Descargar resultados"):
    datos_pdf = {
        "t_llegada": r["t_llegada"],
        "t_atencion": r["t_atencion"],
        "operadores_actuales": r["operadores_actuales"],
        "meta_wq": r["meta_wq"],
    }
    pdf_bytes = generar_pdf(r["nombre"], datos_pdf, actual, rec, economia)
    st.download_button("Descargar resumen ejecutivo en PDF", data=pdf_bytes, file_name="resumen_dimensionamiento_operadores.pdf", mime="application/pdf", use_container_width=True)
    st.download_button("Descargar alternativas en CSV", data=df.to_csv(index=False).encode("utf-8"), file_name="alternativas_operadores.csv", mime="text/csv", use_container_width=True)
