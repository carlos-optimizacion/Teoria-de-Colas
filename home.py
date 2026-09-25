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
        border-radius: 22px;
        padding: 30px 34px;
        color: white;
        box-shadow: 0 12px 30px rgba(23, 50, 77, 0.16);
        margin-bottom: 1.1rem;
    }
    .hero h1 { margin: 0; font-size: 2.25rem; line-height: 1.12; }
    .hero p { margin: .65rem 0 0 0; font-size: 1.02rem; opacity: .93; max-width: 900px; }
    .eyebrow { font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; opacity: .80; }
    .mode-card {
        background: #FFFFFF;
        border: 1px solid #E5EAF0;
        border-radius: 18px;
        padding: 22px 24px;
        min-height: 265px;
        box-shadow: 0 6px 18px rgba(31, 78, 120, 0.06);
    }
    .mode-card h3 { margin-top: 0; color: #17324D; }
    .mode-card p { color: #5A6675; }
    .pill {
        display: inline-block;
        background: #EAF1F7;
        color: #1F4E78;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: .78rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .section-title { color: #17324D; font-weight: 750; margin-top: .5rem; }
    .flow {
        background: #FFFFFF;
        border: 1px solid #E6EBF1;
        border-radius: 16px;
        padding: 16px 18px;
        text-align: center;
        min-height: 105px;
    }
    .flow strong { color: #1F4E78; }
    .small-note { color: #6B7280; font-size: .88rem; }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E6EBF1;
        padding: 14px 16px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(31, 78, 120, 0.04);
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
            Plataforma académica y analítica para comprender, simular y evaluar sistemas de espera.
            Integra aprendizaje progresivo con análisis End-to-End orientado a decisiones operativas y económicas.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Ruta académica", "24 módulos")
k2.metric("Modelos principales", "8+")
k3.metric("Analítica aplicada", "AS IS → TO BE")
k4.metric("Salida ejecutiva", "PDF + escenarios")

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
            <h3>Resolver un sistema real de principio a fin</h3>
            <p>Ruta ejecutiva para transformar datos operativos en diagnóstico, escenarios y una recomendación sustentada.</p>
            <b>Flujo End-to-End</b>
            <ul>
                <li>Definición del problema</li>
                <li>Selección automática del modelo</li>
                <li>Diagnóstico AS IS</li>
                <li>Escenarios TO BE</li>
                <li>Evaluación económica y decisión</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Ruta ejecutiva recomendada")
f1, f2, f3, f4, f5 = st.columns(5)
with f1:
    st.markdown('<div class="flow"><strong>1. Contexto</strong><br><span class="small-note">Llegadas, servicio, capacidad</span></div>', unsafe_allow_html=True)
with f2:
    st.markdown('<div class="flow"><strong>2. Diagnóstico</strong><br><span class="small-note">Utilización, cola, espera</span></div>', unsafe_allow_html=True)
with f3:
    st.markdown('<div class="flow"><strong>3. Escenarios</strong><br><span class="small-note">Capacidad y productividad</span></div>', unsafe_allow_html=True)
with f4:
    st.markdown('<div class="flow"><strong>4. Economía</strong><br><span class="small-note">Costo de capacidad y espera</span></div>', unsafe_allow_html=True)
with f5:
    st.markdown('<div class="flow"><strong>5. Decisión</strong><br><span class="small-note">TO BE y reporte ejecutivo</span></div>', unsafe_allow_html=True)

st.info(
    "Para un análisis aplicado, abre el módulo **25. Análisis End-to-End de Sistemas de Colas** desde el menú lateral. "
    "Si estás aprendiendo el tema, inicia en el módulo 01 y sigue la secuencia."
)

st.markdown("---")
st.caption(
    "Mag. Carlos Alberto Nieto Astahuamán · Aplicación educativa desarrollada con fines académicos. "
    "El análisis automático apoya la toma de decisiones y debe validarse con el contexto operativo real."
)
