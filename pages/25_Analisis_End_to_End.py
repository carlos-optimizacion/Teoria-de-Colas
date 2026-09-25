import streamlit as st
import math
import pandas as pd
import plotly.express as px
from fpdf import FPDF

st.set_page_config(
    page_title="Análisis End-to-End | Teoría de Colas",
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
    .block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1500px; }
    .exec-hero {
        background: linear-gradient(135deg, #163A5F 0%, #1F4E78 58%, #2D6A9F 100%);
        border-radius: 22px;
        padding: 26px 30px;
        color: white;
        box-shadow: 0 12px 28px rgba(23, 50, 77, 0.16);
        margin-bottom: 1rem;
    }
    .exec-hero h1 { margin: 0; font-size: 2.05rem; line-height: 1.15; }
    .exec-hero p { margin: .55rem 0 0; opacity: .92; max-width: 1000px; }
    .eyebrow { font-size: .76rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; opacity: .80; }
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
    .status-ok, .status-warn, .status-critical {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: .78rem;
        font-weight: 750;
        margin-bottom: 8px;
    }
    .status-ok { background: #E9F7EF; color: #166534; }
    .status-warn { background: #FFF7E6; color: #9A6700; }
    .status-critical { background: #FDECEC; color: #B42318; }
    .info-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 15px 17px;
        min-height: 112px;
    }
    .info-card strong { color: #1F4E78; }
    .muted { color: #667085; font-size: .88rem; }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E1E7EE;
        padding: 14px 16px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(31, 78, 120, 0.04);
    }
    div[data-testid="stMetricLabel"] { color: #5B6675; }
    div[data-testid="stMetricValue"] { color: #17324D; }
    div[data-testid="stDataFrame"] {
        border: 1px solid #E1E7EE;
        border-radius: 12px;
        overflow: hidden;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #FFFFFF;
        border: 1px solid #E1E7EE;
        border-radius: 10px 10px 0 0;
        padding: 8px 14px;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Motor matemático
# -----------------------------------------------------------------------------
def _safe_div(a, b):
    if abs(b) < 1e-12:
        return float("inf")
    return a / b


def mm1(lam, mu):
    rho = lam / mu
    if rho >= 1:
        return {
            "modelo": "M/M/1", "estable": False, "rho": rho,
            "L": float("inf"), "Lq": float("inf"), "W": float("inf"), "Wq": float("inf"),
            "P_bloqueo": 0.0, "lambda_efectiva": lam,
        }
    L = rho / (1 - rho)
    Lq = rho**2 / (1 - rho)
    W = 1 / (mu - lam)
    Wq = lam / (mu * (mu - lam))
    return {
        "modelo": "M/M/1", "estable": True, "rho": rho,
        "L": L, "Lq": Lq, "W": W, "Wq": Wq,
        "P_bloqueo": 0.0, "lambda_efectiva": lam,
    }


def mms(lam, mu, s):
    rho = lam / (s * mu)
    if rho >= 1:
        return {
            "modelo": "M/M/s", "estable": False, "rho": rho,
            "L": float("inf"), "Lq": float("inf"), "W": float("inf"), "Wq": float("inf"),
            "P_bloqueo": 0.0, "lambda_efectiva": lam,
        }
    r = lam / mu
    suma = sum((r**n) / math.factorial(n) for n in range(s))
    parte = (r**s) / (math.factorial(s) * (1 - rho))
    p0 = 1 / (suma + parte)
    Lq = (p0 * (r**s) * rho) / (math.factorial(s) * ((1 - rho) ** 2))
    L = Lq + r
    Wq = Lq / lam
    W = Wq + 1 / mu
    return {
        "modelo": "M/M/s", "estable": True, "rho": rho,
        "L": L, "Lq": Lq, "W": W, "Wq": Wq,
        "P_bloqueo": 0.0, "lambda_efectiva": lam,
    }


def mm1k(lam, mu, k):
    rho_nominal = lam / mu
    if abs(rho_nominal - 1.0) < 1e-12:
        probs = [1 / (k + 1)] * (k + 1)
    else:
        p0 = (1 - rho_nominal) / (1 - rho_nominal ** (k + 1))
        probs = [p0 * (rho_nominal**n) for n in range(k + 1)]

    p_bloqueo = probs[-1]
    lam_eff = lam * (1 - p_bloqueo)
    L = sum(n * probs[n] for n in range(k + 1))
    ocupados = lam_eff / mu
    Lq = max(0.0, L - ocupados)
    W = _safe_div(L, lam_eff)
    Wq = _safe_div(Lq, lam_eff)
    rho_efectiva = ocupados
    return {
        "modelo": "M/M/1/K", "estable": True, "rho": rho_efectiva,
        "L": L, "Lq": Lq, "W": W, "Wq": Wq,
        "P_bloqueo": p_bloqueo, "lambda_efectiva": lam_eff,
    }


def mmsk(lam, mu, s, k):
    if k < s:
        raise ValueError("La capacidad total K debe ser mayor o igual al número de servidores.")
    r = lam / mu
    terms = []
    for n in range(k + 1):
        if n < s:
            term = (r**n) / math.factorial(n)
        else:
            term = (r**n) / (math.factorial(s) * (s ** (n - s)))
        terms.append(term)

    p0 = 1 / sum(terms)
    probs = [p0 * t for t in terms]
    p_bloqueo = probs[-1]
    lam_eff = lam * (1 - p_bloqueo)
    L = sum(n * probs[n] for n in range(k + 1))
    ocupados = lam_eff / mu
    Lq = max(0.0, L - ocupados)
    W = _safe_div(L, lam_eff)
    Wq = _safe_div(Lq, lam_eff)
    rho_efectiva = _safe_div(ocupados, s)
    return {
        "modelo": "M/M/s/K", "estable": True, "rho": rho_efectiva,
        "L": L, "Lq": Lq, "W": W, "Wq": Wq,
        "P_bloqueo": p_bloqueo, "lambda_efectiva": lam_eff,
    }


def seleccionar_modelo(s, capacidad_limitada):
    if s == 1 and not capacidad_limitada:
        return "M/M/1"
    if s > 1 and not capacidad_limitada:
        return "M/M/s"
    if s == 1 and capacidad_limitada:
        return "M/M/1/K"
    return "M/M/s/K"


def calcular_modelo(lam, mu, s, capacidad_limitada=False, k=None):
    modelo = seleccionar_modelo(s, capacidad_limitada)
    if modelo == "M/M/1":
        return mm1(lam, mu)
    if modelo == "M/M/s":
        return mms(lam, mu, s)
    if modelo == "M/M/1/K":
        return mm1k(lam, mu, int(k))
    return mmsk(lam, mu, int(s), int(k))


def descomponer_costo(resultado, s, costo_servidor, costo_espera, costo_perdido):
    if not resultado["estable"] or not math.isfinite(resultado["Lq"]):
        return {
            "capacidad": float("inf"), "espera": float("inf"),
            "perdida": float("inf"), "total": float("inf"),
        }
    costo_capacidad = s * costo_servidor
    costo_espera_total = resultado["Lq"] * costo_espera
    if resultado["P_bloqueo"] < 1:
        lambda_original = resultado["lambda_efectiva"] / max(1e-12, 1 - resultado["P_bloqueo"])
        clientes_perdidos_h = max(0.0, lambda_original - resultado["lambda_efectiva"])
    else:
        clientes_perdidos_h = float("inf")
    costo_perdida_total = clientes_perdidos_h * costo_perdido
    total = costo_capacidad + costo_espera_total + costo_perdida_total
    return {
        "capacidad": costo_capacidad,
        "espera": costo_espera_total,
        "perdida": costo_perdida_total,
        "total": total,
    }


def diagnostico(resultado, max_rho, max_wq_min):
    if not resultado["estable"] or not math.isfinite(resultado["Wq"]):
        return "Crítico", "La demanda supera la capacidad de servicio bajo la configuración actual."
    rho_pct = resultado["rho"] * 100
    wq_min = resultado["Wq"] * 60
    if rho_pct > max_rho or wq_min > max_wq_min:
        return (
            "Atención",
            f"La configuración actual excede al menos un umbral gerencial: utilización {rho_pct:.1f}% y espera {wq_min:.1f} min.",
        )
    return (
        "Adecuado",
        f"La configuración actual se mantiene dentro de los umbrales definidos: utilización {rho_pct:.1f}% y espera {wq_min:.1f} min.",
    )


def clean_pdf_text(text):
    return str(text).encode("latin-1", "ignore").decode("latin-1")


def generar_pdf(datos, asis, recomendado, comp, diagnostico_texto, criterio, impacto_mensual):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, clean_pdf_text("Resumen Ejecutivo - Analisis de Sistema de Colas"), ln=True, align="C")
    pdf.ln(3)

    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0, 6,
        clean_pdf_text(
            f"Contexto: {datos['contexto']}\n"
            f"Sistema: {datos['nombre']}\n"
            f"Descripcion: {datos['descripcion']}\n"
            f"Modelo seleccionado: {asis['modelo']}"
        ),
    )

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_pdf_text("1. Diagnostico AS IS"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0, 6,
        clean_pdf_text(
            f"Utilizacion: {asis['rho']*100:.2f}%\n"
            f"Clientes promedio en cola (Lq): {asis['Lq']:.2f}\n"
            f"Espera promedio (Wq): {asis['Wq']*60:.2f} min\n"
            f"Probabilidad de bloqueo: {asis['P_bloqueo']*100:.2f}%\n"
            f"Diagnostico: {diagnostico_texto}"
        ),
    )

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_pdf_text("2. Recomendacion TO BE"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0, 6,
        clean_pdf_text(
            f"Servidores: {int(recomendado['Servidores'])}\n"
            f"Mejora de tasa de servicio: {recomendado['Mejora servicio']}\n"
            f"Utilizacion: {recomendado['Utilizacion %']:.2f}%\n"
            f"Espera Wq: {recomendado['Wq (min)']:.2f} min\n"
            f"Costo total: S/ {recomendado['Costo total (S//h)']:.2f} por hora\n"
            f"Criterio: {criterio}"
        ),
    )

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_pdf_text("3. Impacto ejecutivo"), ln=True)
    pdf.set_font("Arial", "", 10)
    for _, row in comp.iterrows():
        pdf.multi_cell(
            0, 5,
            clean_pdf_text(
                f"{row['Escenario']}: servidores={int(row['Servidores'])}, "
                f"utilizacion={row['Utilizacion %']:.2f}%, Wq={row['Wq (min)']:.2f} min, "
                f"Lq={row['Lq']:.2f}, costo=S/ {row['Costo total (S//h)']:.2f}/h"
            ),
        )
    pdf.multi_cell(0, 6, clean_pdf_text(f"Impacto mensual estimado: S/ {impacto_mensual:+.2f} (positivo = ahorro)."))

    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(
        0, 5,
        clean_pdf_text(
            "Nota: los resultados dependen de los supuestos del modelo y de la calidad de los parametros ingresados. "
            "La recomendacion debe validarse con restricciones operativas reales antes de su implementacion."
        ),
    )

    return bytes(pdf.output(dest="S").encode("latin-1"))


# -----------------------------------------------------------------------------
# Encabezado
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="exec-hero">
        <div class="eyebrow">Decision Support · Investigación de Operaciones</div>
        <h1>Análisis End-to-End de Sistemas de Colas</h1>
        <p>Diagnostica el escenario AS IS, evalúa alternativas TO BE y traduce el desempeño del sistema en una decisión operativa y económica.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Panel lateral de configuración
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Configuración del análisis")
    st.caption("Define el sistema, los objetivos gerenciales y los costos relevantes.")

    with st.form("form_e2e"):
        st.markdown("### 1. Sistema")
        contexto = st.selectbox(
            "Contexto",
            ["Banco", "Hospital / clínica", "Call center", "Logística", "Producción", "Servicios", "Otro"],
        )
        nombre = st.text_input("Nombre del sistema", value="Sistema de atención")
        descripcion = st.text_area(
            "Descripción del problema",
            value="Evaluar el desempeño actual y determinar una configuración de servicio más conveniente.",
            height=90,
        )

        lam = st.number_input("λ · Llegadas por hora", min_value=0.01, value=12.0, step=0.5)
        mu = st.number_input("μ · Servicio por servidor/hora", min_value=0.01, value=8.0, step=0.5)
        s_actual = st.number_input("Servidores actuales", min_value=1, value=2, step=1)
        capacidad_limitada = st.checkbox("Capacidad total limitada")
        K = None
        if capacidad_limitada:
            K = st.number_input(
                "Capacidad total K",
                min_value=int(s_actual),
                value=max(int(s_actual), 10),
                step=1,
            )

        st.markdown("### 2. Objetivos gerenciales")
        objetivo_wq = st.number_input("Wq máximo deseado (min)", min_value=0.0, value=10.0, step=1.0)
        max_rho = st.slider("Utilización máxima (%)", min_value=50, max_value=99, value=90)
        max_extra_servers = st.slider("Servidores adicionales a explorar", min_value=1, max_value=8, value=4)

        st.markdown("### 3. Economía")
        costo_servidor = st.number_input("Costo servidor (S//h)", min_value=0.0, value=20.0, step=1.0)
        costo_espera = st.number_input("Costo espera (S//cliente-h)", min_value=0.0, value=12.0, step=1.0)
        costo_perdido = st.number_input("Costo cliente perdido (S/)", min_value=0.0, value=30.0, step=1.0)
        horas_dia = st.number_input("Horas de operación/día", min_value=1.0, value=8.0, step=1.0)
        dias_mes = st.number_input("Días de operación/mes", min_value=1, value=26, step=1)

        ejecutar = st.form_submit_button("Ejecutar análisis", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# Cálculo y persistencia del análisis
# -----------------------------------------------------------------------------
if ejecutar:
    try:
        asis = calcular_modelo(
            lam=lam,
            mu=mu,
            s=int(s_actual),
            capacidad_limitada=capacidad_limitada,
            k=K,
        )

        estado, texto_diag = diagnostico(asis, max_rho=max_rho, max_wq_min=objetivo_wq)
        modelo_sugerido = seleccionar_modelo(int(s_actual), capacidad_limitada)

        escenarios = []
        mejoras_servicio = [1.00, 1.10, 1.20, 1.30]
        inicio_s = max(1, int(s_actual) - 1)
        fin_s = int(s_actual) + int(max_extra_servers)

        for s_eval in range(inicio_s, fin_s + 1):
            for factor in mejoras_servicio:
                mu_eval = mu * factor
                k_eval = max(int(K), s_eval) if capacidad_limitada else None
                resultado = calcular_modelo(
                    lam=lam,
                    mu=mu_eval,
                    s=s_eval,
                    capacidad_limitada=capacidad_limitada,
                    k=k_eval,
                )
                costos = descomponer_costo(
                    resultado,
                    s=s_eval,
                    costo_servidor=costo_servidor,
                    costo_espera=costo_espera,
                    costo_perdido=costo_perdido,
                )
                if resultado["estable"] and math.isfinite(resultado["Wq"]) and math.isfinite(costos["total"]):
                    escenarios.append(
                        {
                            "Servidores": s_eval,
                            "Mejora servicio": f"+{int(round((factor-1)*100))}%",
                            "μ": round(mu_eval, 3),
                            "Utilización %": round(resultado["rho"] * 100, 2),
                            "L": round(resultado["L"], 3),
                            "Lq": round(resultado["Lq"], 3),
                            "W (min)": round(resultado["W"] * 60, 3),
                            "Wq (min)": round(resultado["Wq"] * 60, 3),
                            "Bloqueo %": round(resultado["P_bloqueo"] * 100, 3),
                            "Costo capacidad (S//h)": round(costos["capacidad"], 2),
                            "Costo espera (S//h)": round(costos["espera"], 2),
                            "Costo pérdida (S//h)": round(costos["perdida"], 2),
                            "Costo total (S//h)": round(costos["total"], 2),
                        }
                    )

        if not escenarios:
            st.error("No fue posible generar escenarios factibles con los parámetros ingresados.")
        else:
            df = pd.DataFrame(escenarios)
            factibles = df[
                (df["Wq (min)"] <= objetivo_wq)
                & (df["Utilización %"] <= max_rho)
            ].copy()

            if not factibles.empty:
                recomendado = factibles.sort_values(
                    ["Costo total (S//h)", "Wq (min)", "Servidores"]
                ).iloc[0].to_dict()
                criterio = "cumple los objetivos de espera y utilización con el menor costo total entre los escenarios factibles"
                cumple_objetivos = True
            else:
                aux = df.copy()
                base_wq = max(objetivo_wq, 1.0)
                base_rho = max(float(max_rho), 1.0)
                aux["Brecha gerencial"] = (
                    (aux["Wq (min)"] - objetivo_wq).clip(lower=0) / base_wq
                    + (aux["Utilización %"] - max_rho).clip(lower=0) / base_rho
                )
                recomendado = aux.sort_values(
                    ["Brecha gerencial", "Costo total (S//h)", "Wq (min)"]
                ).iloc[0].to_dict()
                criterio = "minimiza la brecha respecto de los objetivos gerenciales y, en segundo lugar, el costo total"
                cumple_objetivos = False

            costos_asis = descomponer_costo(
                asis,
                s=int(s_actual),
                costo_servidor=costo_servidor,
                costo_espera=costo_espera,
                costo_perdido=costo_perdido,
            )

            comp = pd.DataFrame(
                [
                    {
                        "Escenario": "AS IS",
                        "Servidores": int(s_actual),
                        "Utilización %": round(asis["rho"] * 100, 2) if math.isfinite(asis["rho"]) else float("inf"),
                        "Wq (min)": round(asis["Wq"] * 60, 2) if math.isfinite(asis["Wq"]) else float("inf"),
                        "Lq": round(asis["Lq"], 2) if math.isfinite(asis["Lq"]) else float("inf"),
                        "Costo total (S//h)": round(costos_asis["total"], 2),
                    },
                    {
                        "Escenario": "TO BE",
                        "Servidores": int(recomendado["Servidores"]),
                        "Utilización %": float(recomendado["Utilización %"]),
                        "Wq (min)": float(recomendado["Wq (min)"]),
                        "Lq": float(recomendado["Lq"]),
                        "Costo total (S//h)": float(recomendado["Costo total (S//h)"]),
                    },
                ]
            )

            if math.isfinite(costos_asis["total"]):
                ahorro_hora = costos_asis["total"] - float(recomendado["Costo total (S//h)"])
                impacto_mensual = ahorro_hora * horas_dia * dias_mes
            else:
                ahorro_hora = float("nan")
                impacto_mensual = float("nan")

            st.session_state["e2e_resultado"] = {
                "contexto": contexto,
                "nombre": nombre,
                "descripcion": descripcion,
                "lam": lam,
                "mu": mu,
                "s_actual": int(s_actual),
                "capacidad_limitada": capacidad_limitada,
                "K": int(K) if K is not None else None,
                "modelo_sugerido": modelo_sugerido,
                "asis": asis,
                "estado": estado,
                "texto_diag": texto_diag,
                "df": df,
                "recomendado": recomendado,
                "criterio": criterio,
                "cumple_objetivos": cumple_objetivos,
                "comp": comp,
                "costos_asis": costos_asis,
                "objetivo_wq": objetivo_wq,
                "max_rho": max_rho,
                "horas_dia": horas_dia,
                "dias_mes": dias_mes,
                "ahorro_hora": ahorro_hora,
                "impacto_mensual": impacto_mensual,
            }

    except Exception as exc:
        st.error(f"No fue posible completar el análisis: {exc}")
        st.caption("Verifica que λ, μ, servidores y capacidad K sean coherentes.")

# -----------------------------------------------------------------------------
# Estado inicial
# -----------------------------------------------------------------------------
if "e2e_resultado" not in st.session_state:
    st.markdown("### Cómo funciona")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="info-card"><strong>1. Configura</strong><br><span class="muted">Define llegadas, servicio, capacidad, objetivos y costos.</span></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="info-card"><strong>2. Diagnostica</strong><br><span class="muted">Obtén utilización, cola, espera y estado AS IS.</span></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="info-card"><strong>3. Evalúa</strong><br><span class="muted">Compara escenarios de servidores y mejora del servicio.</span></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="info-card"><strong>4. Decide</strong><br><span class="muted">Selecciona un TO BE y cuantifica el impacto económico.</span></div>', unsafe_allow_html=True)

    st.markdown("### Enfoque gerencial")
    st.info(
        "El análisis no busca únicamente reducir la espera. La decisión combina nivel de servicio, utilización de capacidad y costo total. "
        "Los costos ingresados deben representar el contexto real de la organización."
    )
    st.stop()

# -----------------------------------------------------------------------------
# Dashboard de resultados
# -----------------------------------------------------------------------------
r = st.session_state["e2e_resultado"]
asis = r["asis"]
df = r["df"]
recomendado = r["recomendado"]
comp = r["comp"]

status_class = {
    "Adecuado": "status-ok",
    "Atención": "status-warn",
    "Crítico": "status-critical",
}.get(r["estado"], "status-warn")

st.markdown(
    f"""
    <div class="decision-card">
        <span class="{status_class}">AS IS · {r['estado']}</span>
        <h3>{r['nombre']} · {r['contexto']}</h3>
        <p><b>Modelo:</b> {r['modelo_sugerido']} &nbsp; | &nbsp; <b>λ:</b> {r['lam']:.2f}/h &nbsp; | &nbsp; <b>μ:</b> {r['mu']:.2f}/h por servidor &nbsp; | &nbsp; <b>Servidores:</b> {r['s_actual']}</p>
        <p>{r['texto_diag']}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

resumen_tab, escenarios_tab, economia_tab, reporte_tab = st.tabs(
    ["Resumen ejecutivo", "Escenarios", "Economía", "Reporte"]
)

with resumen_tab:
    st.markdown("### Indicadores AS IS")
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("Utilización", f"{asis['rho']*100:.1f}%")
    a2.metric("Clientes en cola", f"{asis['Lq']:.2f}" if math.isfinite(asis['Lq']) else "∞")
    a3.metric("Espera Wq", f"{asis['Wq']*60:.2f} min" if math.isfinite(asis['Wq']) else "∞")
    a4.metric("Tiempo total W", f"{asis['W']*60:.2f} min" if math.isfinite(asis['W']) else "∞")
    a5.metric("Bloqueo", f"{asis['P_bloqueo']*100:.2f}%")

    st.markdown("### Recomendación TO BE")
    asis_wq = asis["Wq"] * 60 if math.isfinite(asis["Wq"]) else float("nan")
    tobe_wq = float(recomendado["Wq (min)"])
    delta_wq = tobe_wq - asis_wq if math.isfinite(asis_wq) else float("nan")

    asis_cost = float(r["costos_asis"]["total"])
    tobe_cost = float(recomendado["Costo total (S//h)"])
    delta_cost = tobe_cost - asis_cost if math.isfinite(asis_cost) else float("nan")

    t1, t2, t3, t4, t5 = st.columns(5)
    t1.metric("Servidores TO BE", int(recomendado["Servidores"]), delta=int(recomendado["Servidores"]) - r["s_actual"])
    t2.metric("Mejora de μ", recomendado["Mejora servicio"])
    t3.metric("Utilización TO BE", f"{recomendado['Utilización %']:.1f}%")
    t4.metric("Wq TO BE", f"{tobe_wq:.2f} min", delta=f"{delta_wq:+.2f} min" if math.isfinite(delta_wq) else None, delta_color="inverse")
    t5.metric("Costo TO BE", f"S/ {tobe_cost:.2f}/h", delta=f"S/ {delta_cost:+.2f}/h" if math.isfinite(delta_cost) else None, delta_color="inverse")

    if r["cumple_objetivos"]:
        estado_rec = "Cumple objetivos"
        clase_rec = "status-ok"
    else:
        estado_rec = "Mejor alternativa disponible"
        clase_rec = "status-warn"

    impacto_txt = (
        f"S/ {r['impacto_mensual']:+,.2f} por mes" if math.isfinite(r["impacto_mensual"]) else "No calculable con AS IS inestable"
    )

    st.markdown(
        f"""
        <div class="decision-card">
            <span class="{clase_rec}">{estado_rec}</span>
            <h3>Decisión sugerida</h3>
            <p>Evaluar una configuración con <b>{int(recomendado['Servidores'])} servidor(es)</b> y una mejora de tasa de servicio de <b>{recomendado['Mejora servicio']}</b>.</p>
            <p>La selección {r['criterio']}.</p>
            <p><b>Impacto económico mensual estimado:</b> {impacto_txt} <span class="muted">(positivo = ahorro frente al AS IS)</span></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### AS IS vs TO BE")
    st.dataframe(comp, use_container_width=True, hide_index=True)

    tradeoff = px.scatter(
        df,
        x="Wq (min)",
        y="Costo total (S//h)",
        size="Servidores",
        color="Mejora servicio",
        hover_data=["Servidores", "Utilización %", "Lq", "Bloqueo %"],
        title="Mapa de decisión: nivel de servicio vs costo",
        template="plotly_white",
    )
    tradeoff.add_vline(x=r["objetivo_wq"], line_dash="dash", annotation_text="Objetivo Wq")
    st.plotly_chart(tradeoff, use_container_width=True)

with escenarios_tab:
    st.markdown("### Portafolio de escenarios TO BE")
    st.caption("Ordena y filtra la tabla para revisar el compromiso entre capacidad, espera, utilización y costo.")

    vista = df.copy()
    vista["Cumple Wq"] = vista["Wq (min)"] <= r["objetivo_wq"]
    vista["Cumple utilización"] = vista["Utilización %"] <= r["max_rho"]
    vista["Factible gerencial"] = vista["Cumple Wq"] & vista["Cumple utilización"]
    vista = vista.sort_values(["Factible gerencial", "Costo total (S//h)", "Wq (min)"], ascending=[False, True, True])
    st.dataframe(vista, use_container_width=True, hide_index=True)

    g1, g2 = st.columns(2)
    with g1:
        fig_wq = px.line(
            df,
            x="Servidores",
            y="Wq (min)",
            color="Mejora servicio",
            markers=True,
            title="Espera promedio por configuración",
            template="plotly_white",
        )
        fig_wq.add_hline(y=r["objetivo_wq"], line_dash="dash", annotation_text="Objetivo")
        st.plotly_chart(fig_wq, use_container_width=True)
    with g2:
        fig_rho = px.line(
            df,
            x="Servidores",
            y="Utilización %",
            color="Mejora servicio",
            markers=True,
            title="Utilización por configuración",
            template="plotly_white",
        )
        fig_rho.add_hline(y=r["max_rho"], line_dash="dash", annotation_text="Máximo deseado")
        st.plotly_chart(fig_rho, use_container_width=True)

with economia_tab:
    st.markdown("### Estructura económica de la decisión")
    costos_asis = r["costos_asis"]
    costos_tobe = {
        "capacidad": float(recomendado["Costo capacidad (S//h)"]),
        "espera": float(recomendado["Costo espera (S//h)"]),
        "perdida": float(recomendado["Costo pérdida (S//h)"]),
        "total": float(recomendado["Costo total (S//h)"]),
    }

    eco1, eco2, eco3, eco4 = st.columns(4)
    eco1.metric("Costo AS IS", f"S/ {costos_asis['total']:.2f}/h" if math.isfinite(costos_asis['total']) else "∞")
    eco2.metric("Costo TO BE", f"S/ {costos_tobe['total']:.2f}/h")
    eco3.metric("Impacto por hora", f"S/ {r['ahorro_hora']:+.2f}" if math.isfinite(r["ahorro_hora"]) else "N/D")
    eco4.metric("Impacto mensual", f"S/ {r['impacto_mensual']:+,.2f}" if math.isfinite(r["impacto_mensual"]) else "N/D")

    costos_plot = pd.DataFrame(
        [
            {"Escenario": "AS IS", "Componente": "Capacidad", "Costo": costos_asis["capacidad"]},
            {"Escenario": "AS IS", "Componente": "Espera", "Costo": costos_asis["espera"]},
            {"Escenario": "AS IS", "Componente": "Pérdida", "Costo": costos_asis["perdida"]},
            {"Escenario": "TO BE", "Componente": "Capacidad", "Costo": costos_tobe["capacidad"]},
            {"Escenario": "TO BE", "Componente": "Espera", "Costo": costos_tobe["espera"]},
            {"Escenario": "TO BE", "Componente": "Pérdida", "Costo": costos_tobe["perdida"]},
        ]
    )
    costos_plot = costos_plot.replace([float("inf"), -float("inf")], pd.NA).dropna()
    fig_costos = px.bar(
        costos_plot,
        x="Escenario",
        y="Costo",
        color="Componente",
        barmode="stack",
        title="Composición del costo operativo por hora",
        template="plotly_white",
    )
    st.plotly_chart(fig_costos, use_container_width=True)

    st.caption(
        f"Proyección mensual calculada con {r['horas_dia']:.0f} horas/día y {r['dias_mes']} días/mes. "
        "El impacto es una estimación y depende de la validez de los costos de espera, capacidad y pérdida ingresados."
    )

with reporte_tab:
    st.markdown("### Reporte y trazabilidad")

    datos_reporte = {
        "contexto": r["contexto"],
        "nombre": r["nombre"],
        "descripcion": r["descripcion"],
    }

    if asis["estable"] and math.isfinite(asis["Wq"]):
        pdf_bytes = generar_pdf(
            datos=datos_reporte,
            asis=asis,
            recomendado=recomendado,
            comp=comp,
            diagnostico_texto=r["texto_diag"],
            criterio=r["criterio"],
            impacto_mensual=r["impacto_mensual"],
        )
        st.download_button(
            "Descargar resumen ejecutivo en PDF",
            data=pdf_bytes,
            file_name="resumen_ejecutivo_teoria_colas.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.warning("El PDF ejecutivo se habilita cuando el escenario AS IS tiene métricas finitas.")

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar matriz de escenarios en CSV",
        data=csv_data,
        file_name="escenarios_teoria_colas.csv",
        mime="text/csv",
        use_container_width=True,
    )

    with st.expander("Supuestos del análisis", expanded=True):
        st.markdown(
            """
            - Las tasas de llegada y servicio se expresan por hora.
            - Los modelos M/M/1 y M/M/s requieren utilización menor que 100% para estabilidad.
            - Los modelos con capacidad finita consideran bloqueo cuando el sistema alcanza K.
            - La estructura de costos es una aproximación gerencial y debe parametrizarse con información real.
            - La recomendación automática funciona como soporte de decisión; no sustituye la validación operativa.
            - Debe verificarse que los supuestos probabilísticos del modelo representen adecuadamente el sistema analizado.
            """
        )

    st.markdown("### Criterio de selección")
    st.write(r["criterio"].capitalize() + ".")
