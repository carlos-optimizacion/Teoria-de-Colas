import streamlit as st

st.set_page_config(
    page_title="Teoría de Colas | Decision Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #F6F8FB; }
    .block-container { padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1450px; }
    .hero {
        background: linear-gradient(135deg, #163A5F 0%, #1F4E78 58%, #2D6A9F 100%);
        border-radius: 22px; padding: 30px 34px; color: white;
        box-shadow: 0 12px 30px rgba(23, 50, 77, 0.16); margin-bottom: 1.1rem;
    }
    .hero h1 { margin: 0; font-size: 2.25rem; line-height: 1.12; }
    .hero p { margin: .65rem 0 0 0; font-size: 1.02rem; opacity: .93; max-width: 950px; }
    .eyebrow { font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; opacity: .80; }
    .mode-card {
        background: #FFFFFF; border: 1px solid #E5EAF0; border-radius: 18px;
        padding: 22px 24px; min-height: 270px; box-shadow: 0 6px 18px rgba(31,78,120,.06);
    }
    .mode-card h3 { margin-top: 0; color: #17324D; }
    .mode-card p { color: #5A6675; }
    .pill {
        display: inline-block; background: #EAF1F7; color: #1F4E78; border-radius: 999px;
        padding: 5px 10px; font-size: .78rem; font-weight: 700; margin-bottom: 8px;
    }
    .flow {
        background: #FFFFFF; border: 1px solid #E6EBF1; border-radius: 16px;
        padding: 16px 18px; text-align: center; min-height: 105px;
    }
    .flow strong { color: #1F4E78; }
    .small-note { color: #6B7280; font-size: .88rem; }
    div[data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E6EBF1; padding: 14px 16px;
        border-radius: 14px; box-shadow: 0 4px 12px rgba(31,78,120,.04);
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Investigación de Operaciones · Ingeniería Industrial</div>
        <h1>Teoría de Colas | Decision Lab</h1>
        <p>
            Plataforma académica para aprender teoría de colas y herramienta analítica para dimensionar
            operadores, estimar tiempos de espera y evaluar el costo-beneficio del nivel de servicio.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Ruta académica", "24 módulos")
k2.metric("Modelos principales", "8+")
k3.metric("Modo analista", "Dotación óptima")
k4.metric("Salida ejecutiva", "PDF + alternativas")

st.markdown("### Elige tu ruta")
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        """
        <div class="mode-card">
            <span class="pill">MODO APRENDIZAJE</span>
            <h3>Aprender y practicar teoría de colas</h3>
            <p>Ruta secuencial para desarrollar conceptos, resolver ejemplos, practicar modelos y verificar el aprendizaje.</p>
            <b>Incluye</b>
            <ul>
                <li>Fundamentos y notación de Kendall</li>
                <li>M/M/1, M/M/s y modelos con capacidad limitada</li>
                <li>M/G/1 y modelo determinista</li>
                <li>Casos prácticos y autoevaluaciones</li>
                <li>Evaluación final</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="mode-card">
            <span class="pill">MODO ANALISTA</span>
            <h3>Dimensionar operadores para un sistema real</h3>
            <p>Ingresa datos que un responsable de operaciones conoce: cada cuánto llegan clientes, cuánto demora atenderlos y cuántos operadores tiene.</p>
            <b>La herramienta responde</b>
            <ul>
                <li>¿La dotación actual soporta la demanda?</li>
                <li>¿Cuánto espera el cliente?</li>
                <li>¿Cuántos operadores conviene evaluar?</li>
                <li>¿Qué dotación cumple la meta de servicio?</li>
                <li>¿Cuál es el costo-beneficio de mejorar la atención?</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Ruta gerencial del Modo Analista")
f1, f2, f3, f4 = st.columns(4)
with f1:
    st.markdown('<div class="flow"><strong>1. Llegadas y atención</strong><br><span class="small-note">Datos reales del proceso</span></div>', unsafe_allow_html=True)
with f2:
    st.markdown('<div class="flow"><strong>2. Dotación</strong><br><span class="small-note">Operadores actuales y rango</span></div>', unsafe_allow_html=True)
with f3:
    st.markdown('<div class="flow"><strong>3. Servicio</strong><br><span class="small-note">Espera y probabilidad de cola</span></div>', unsafe_allow_html=True)
with f4:
    st.markdown('<div class="flow"><strong>4. Decisión</strong><br><span class="small-note">Costo-beneficio y recomendación</span></div>', unsafe_allow_html=True)

st.info(
    "Para dimensionar un sistema real, abre el módulo **25. Análisis End-to-End de Sistemas de Colas** desde el menú lateral. "
    "Si estás aprendiendo el tema, inicia en el módulo 01 y sigue la secuencia."
)

st.markdown("---")
st.caption(
    "Mag. Carlos Alberto Nieto Astahuamán · Aplicación educativa desarrollada con fines académicos. "
    "La recomendación automática funciona como apoyo a la decisión y debe validarse con el contexto operativo real."
)
