import streamlit as st

st.set_page_config(
    page_title="02 - Modelo M/M/1",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Estilo pedagógico
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background: #F7F9FC; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1400px; }
    .hero-learn {
        background: linear-gradient(135deg, #153A5B 0%, #1F5A86 100%);
        border-radius: 22px;
        padding: 28px 32px;
        color: white;
        box-shadow: 0 12px 28px rgba(23,50,77,.14);
        margin-bottom: 1rem;
    }
    .hero-learn h1 { margin: 0; font-size: 2.05rem; }
    .hero-learn p { margin: .65rem 0 0; opacity: .94; max-width: 980px; }
    .eyebrow { font-size: .77rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; opacity: .82; }
    .learn-card {
        background: white;
        border: 1px solid #E3E9F0;
        border-radius: 16px;
        padding: 18px 20px;
        min-height: 130px;
        box-shadow: 0 4px 14px rgba(31,78,120,.05);
    }
    .learn-card h4 { margin: 0 0 .4rem; color: #17324D; }
    .learn-card p { margin: 0; color: #5A6675; }
    .concept-card {
        background: #FFFFFF;
        border: 1px solid #E3E9F0;
        border-radius: 14px;
        padding: 16px 18px;
        min-height: 135px;
    }
    .concept-card .symbol { font-size: 1.5rem; font-weight: 800; color: #1F5A86; }
    .concept-card .label { font-weight: 700; color: #17324D; }
    .concept-card .desc { color: #667085; font-size: .92rem; }
    .queue-panel {
        background: #FFFFFF;
        border: 1px solid #E3E9F0;
        border-radius: 18px;
        padding: 22px;
        margin: .4rem 0 1rem;
        box-shadow: 0 5px 16px rgba(31,78,120,.05);
    }
    .queue-flow {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 14px;
    }
    .node {
        background: #F0F5FA;
        border: 1px solid #CEDBE8;
        border-radius: 14px;
        padding: 14px 18px;
        text-align: center;
        min-width: 125px;
        color: #17324D;
        font-weight: 700;
    }
    .server {
        background: #EAF7EF;
        border: 1px solid #C8E4D1;
    }
    .arrow { font-size: 1.5rem; color: #65758B; font-weight: 800; }
    .warning-box {
        background: #FFF7E6;
        border: 1px solid #F0D9AB;
        border-left: 6px solid #D97706;
        border-radius: 14px;
        padding: 15px 18px;
        margin: .4rem 0 1rem;
        color: #75440A;
    }
    .success-box {
        background: #EAF7EF;
        border: 1px solid #C8E4D1;
        border-left: 6px solid #15803D;
        border-radius: 14px;
        padding: 15px 18px;
        margin: .4rem 0 1rem;
        color: #14532D;
    }
    .example-box {
        background: #FFFFFF;
        border: 1px solid #DDE5EC;
        border-left: 6px solid #1F5A86;
        border-radius: 16px;
        padding: 18px 20px;
        margin: .5rem 0 1rem;
    }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E1E7EE;
        padding: 14px 16px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(31,78,120,.04);
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Encabezado
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-learn">
        <div class="eyebrow">Modo Aprendizaje · Teoría de Colas</div>
        <h1>02. Modelo M/M/1</h1>
        <p>
            Aprende a reconocer un sistema con una sola estación de servicio, convertir tiempos reales
            en tasas de llegada y atención, calcular sus indicadores y, sobre todo, interpretar qué significan
            para la operación.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 1. Objetivos de aprendizaje
# -----------------------------------------------------------------------------
st.markdown("## 1. ¿Qué aprenderás?")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="learn-card"><h4>🔎 Reconocer</h4><p>Identificar cuándo un proceso puede representarse como M/M/1.</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="learn-card"><h4>🔄 Convertir</h4><p>Pasar de minutos entre llegadas y atención a tasas λ y μ.</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="learn-card"><h4>🧮 Calcular</h4><p>Obtener utilización, cola, espera y permanencia en el sistema.</p></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="learn-card"><h4>💡 Interpretar</h4><p>Traducir los resultados matemáticos en decisiones operativas.</p></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Visual del sistema
# -----------------------------------------------------------------------------
st.markdown("## 2. Primero visualiza el sistema")
st.markdown(
    """
    <div class="queue-panel">
        <b>Ejemplo:</b> una ventanilla de atención con una sola fila y un solo trabajador.
        <div class="queue-flow">
            <div class="node">👥 Llegadas<br><small>clientes</small></div>
            <div class="arrow">→</div>
            <div class="node">🧍🧍🧍 Cola<br><small>espera</small></div>
            <div class="arrow">→</div>
            <div class="node server">👤 1 servidor<br><small>atiende uno a la vez</small></div>
            <div class="arrow">→</div>
            <div class="node">✅ Salida<br><small>cliente atendido</small></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    El modelo **M/M/1** representa un sistema en el que las llegadas son aleatorias, los tiempos de servicio
    también son variables y existe **un solo servidor**. La notación se interpreta así:

    - Primer **M**: llegadas aleatorias compatibles con un proceso Poisson; los tiempos entre llegadas son exponenciales.
    - Segundo **M**: tiempos de servicio exponenciales.
    - **1**: existe un único servidor.

    En su forma clásica se asume una sola cola, disciplina FIFO, población potencial grande y capacidad de espera no limitada.
    """
)

# -----------------------------------------------------------------------------
# 3. Variables en lenguaje simple
# -----------------------------------------------------------------------------
st.markdown("## 3. Entiende las variables antes de usar fórmulas")
v1, v2, v3, v4 = st.columns(4)
with v1:
    st.markdown('<div class="concept-card"><div class="symbol">λ</div><div class="label">Tasa de llegada</div><div class="desc">Cuántos clientes llegan por unidad de tiempo.</div></div>', unsafe_allow_html=True)
with v2:
    st.markdown('<div class="concept-card"><div class="symbol">μ</div><div class="label">Tasa de servicio</div><div class="desc">Cuántos clientes puede atender el servidor por unidad de tiempo.</div></div>', unsafe_allow_html=True)
with v3:
    st.markdown('<div class="concept-card"><div class="symbol">ρ</div><div class="label">Utilización</div><div class="desc">Qué proporción del tiempo está ocupado el servidor.</div></div>', unsafe_allow_html=True)
with v4:
    st.markdown('<div class="concept-card"><div class="symbol">Wq</div><div class="label">Espera en cola</div><div class="desc">Cuánto tiempo espera un cliente antes de ser atendido.</div></div>', unsafe_allow_html=True)

st.markdown("### De tiempos reales a tasas")
st.markdown(
    """
    En una operación real normalmente conoces **minutos**, no tasas. Por eso conviene empezar desde los tiempos observados:

    \[
    \lambda = \frac{60}{\text{minutos entre llegadas}}
    \qquad
    \mu = \frac{60}{\text{minutos por atención}}
    \]

    Ejemplo: si llega un cliente cada 6 minutos, entonces \(\lambda = 10\) clientes/hora.  
    Si una atención dura 4 minutos, entonces \(\mu = 15\) clientes/hora.
    """
)

# -----------------------------------------------------------------------------
# 4. Regla clave de estabilidad
# -----------------------------------------------------------------------------
st.markdown("## 4. La regla más importante")
st.latex(r"\rho = \frac{\lambda}{\mu}")
st.markdown(
    """
    Para que el sistema M/M/1 sea estable debe cumplirse:
    """
)
st.latex(r"\lambda < \mu \quad \Longleftrightarrow \quad \rho < 1")

st.markdown(
    """
    <div class="warning-box">
        <b>⚠️ Atención:</b> que λ sea menor que μ no significa que nunca habrá cola. Las llegadas y los tiempos de servicio son aleatorios,
        por lo que pueden producirse esperas aun cuando el servidor tenga capacidad promedio suficiente. Si λ ≥ μ, en cambio,
        la demanda iguala o supera la capacidad y la cola tenderá a crecer sin límite en el modelo clásico.
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 5. Fórmulas esenciales
# -----------------------------------------------------------------------------
st.markdown("## 5. Fórmulas esenciales")
f1, f2 = st.columns(2)
with f1:
    st.markdown("**Clientes promedio**")
    st.latex(r"L = \frac{\rho}{1-\rho}")
    st.latex(r"L_q = \frac{\rho^2}{1-\rho}")
    st.caption("L incluye cola + cliente en servicio. Lq considera solo quienes esperan.")
with f2:
    st.markdown("**Tiempos promedio**")
    st.latex(r"W = \frac{1}{\mu-\lambda}")
    st.latex(r"W_q = \frac{\lambda}{\mu(\mu-\lambda)}")
    st.caption("W incluye espera + atención. Wq es solo el tiempo en cola.")

st.markdown("También se cumple la **Ley de Little**:")
st.latex(r"L = \lambda W \qquad ; \qquad L_q = \lambda W_q")

# -----------------------------------------------------------------------------
# 6. Ejemplo guiado paso a paso
# -----------------------------------------------------------------------------
st.markdown("## 6. Ejemplo guiado: ventanilla de atención")
st.markdown(
    """
    <div class="example-box">
        <b>Situación:</b> en una ventanilla llega, en promedio, un cliente cada <b>6 minutos</b> y la atención tarda
        <b>4 minutos</b>. Hay un solo trabajador. Queremos conocer qué tan ocupado está, cuántas personas esperan y cuánto tiempo
        permanece un cliente en el sistema.
    </div>
    """,
    unsafe_allow_html=True,
)

# Datos del ejemplo
te_llegada = 6.0
te_servicio = 4.0
lambda_e = 60 / te_llegada
mu_e = 60 / te_servicio
rho_e = lambda_e / mu_e
L_e = rho_e / (1 - rho_e)
Lq_e = rho_e**2 / (1 - rho_e)
W_e = 1 / (mu_e - lambda_e)
Wq_e = lambda_e / (mu_e * (mu_e - lambda_e))

paso1, paso2, paso3 = st.tabs(["Paso 1 · Convertir datos", "Paso 2 · Calcular", "Paso 3 · Interpretar"])

with paso1:
    st.markdown("**Llegadas**")
    st.latex(r"\lambda = \frac{60}{6} = 10\ clientes/hora")
    st.markdown("**Servicio**")
    st.latex(r"\mu = \frac{60}{4} = 15\ clientes/hora")
    st.success("Como 10 < 15, el sistema es estable y podemos aplicar las fórmulas M/M/1.")

with paso2:
    e1, e2, e3, e4, e5 = st.columns(5)
    e1.metric("Utilización ρ", f"{rho_e*100:.1f}%")
    e2.metric("L", f"{L_e:.2f}")
    e3.metric("Lq", f"{Lq_e:.2f}")
    e4.metric("W", f"{W_e*60:.1f} min")
    e5.metric("Wq", f"{Wq_e*60:.1f} min")

    with st.expander("Ver sustitución en las fórmulas"):
        st.latex(r"\rho = \frac{10}{15} = 0.667")
        st.latex(r"L = \frac{0.667}{1-0.667} \approx 2.00")
        st.latex(r"L_q = \frac{0.667^2}{1-0.667} \approx 1.33")
        st.latex(r"W = \frac{1}{15-10} = 0.20\ h = 12\ min")
        st.latex(r"W_q = 0.1333\ h = 8\ min")

with paso3:
    st.markdown(
        """
        <div class="success-box">
            <b>Lectura operativa del resultado:</b><br><br>
            El trabajador está ocupado aproximadamente el <b>66.7 % del tiempo</b>. En promedio hay <b>1.33 clientes esperando</b>
            y cada cliente permanece alrededor de <b>12 minutos</b> en el sistema, de los cuales <b>8 minutos corresponden a espera</b>.
            Aunque la capacidad promedio es suficiente, la variabilidad de las llegadas y del servicio genera cola.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("Pregunta de gestión: si la empresa promete atender en menos de 5 minutos de espera, esta configuración no cumple el nivel de servicio esperado.")

# -----------------------------------------------------------------------------
# 7. Experimenta tú mismo
# -----------------------------------------------------------------------------
st.markdown("## 7. Experimenta tú mismo")
st.caption("Modifica tiempos reales y observa cómo cambia el comportamiento del sistema.")

x1, x2 = st.columns(2)
with x1:
    t_llegada = st.slider("Un cliente llega cada... (min)", min_value=1.0, max_value=20.0, value=6.0, step=0.5)
with x2:
    t_servicio = st.slider("Cada atención tarda... (min)", min_value=1.0, max_value=20.0, value=4.0, step=0.5)

lambda_u = 60 / t_llegada
mu_u = 60 / t_servicio
rho_u = lambda_u / mu_u

st.markdown(f"**Equivalencia:** λ = {lambda_u:.2f} clientes/hora · μ = {mu_u:.2f} clientes/hora")

if rho_u >= 1:
    st.error(
        f"Sistema inestable: la utilización sería {rho_u*100:.1f} %. La capacidad del único servidor no alcanza para absorber la demanda promedio."
    )
else:
    L_u = rho_u / (1 - rho_u)
    Lq_u = rho_u**2 / (1 - rho_u)
    W_u = 1 / (mu_u - lambda_u)
    Wq_u = lambda_u / (mu_u * (mu_u - lambda_u))

    u1, u2, u3, u4, u5 = st.columns(5)
    u1.metric("Utilización", f"{rho_u*100:.1f}%")
    u2.metric("L", f"{L_u:.2f}")
    u3.metric("Lq", f"{Lq_u:.2f}")
    u4.metric("W", f"{W_u*60:.2f} min")
    u5.metric("Wq", f"{Wq_u*60:.2f} min")

    if rho_u >= 0.85:
        st.warning("El sistema es estable, pero opera con alta utilización. Pequeños incrementos en la demanda pueden aumentar considerablemente la espera.")
    elif rho_u >= 0.70:
        st.info("La utilización es moderada-alta. Conviene revisar si el tiempo de espera cumple el nivel de servicio esperado.")
    else:
        st.success("La capacidad promedio es holgada. Revisa si el costo de mantener capacidad ociosa es aceptable para la operación.")

# -----------------------------------------------------------------------------
# 8. Errores frecuentes
# -----------------------------------------------------------------------------
st.markdown("## 8. Errores frecuentes")
er1, er2, er3 = st.columns(3)
with er1:
    st.markdown('<div class="learn-card"><h4>❌ Confundir tiempo con tasa</h4><p>6 min entre llegadas no significa λ = 6. Significa λ = 60/6 = 10 clientes/h.</p></div>', unsafe_allow_html=True)
with er2:
    st.markdown('<div class="learn-card"><h4>❌ Aplicar el modelo si ρ ≥ 1</h4><p>En M/M/1, si la demanda iguala o supera la capacidad, las métricas de estado estable dejan de ser válidas.</p></div>', unsafe_allow_html=True)
with er3:
    st.markdown('<div class="learn-card"><h4>❌ Mirar solo la utilización</h4><p>Una utilización aceptable no garantiza un buen servicio. También deben revisarse Wq y Lq.</p></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. Mini comprobación
# -----------------------------------------------------------------------------
st.markdown("## 9. Comprueba lo aprendido")
with st.expander("Mini quiz de 3 preguntas", expanded=False):
    q1 = st.radio(
        "1. Si llega un cliente cada 5 minutos, ¿cuál es λ?",
        ["5 clientes/h", "12 clientes/h", "60 clientes/h"],
        key="mm1_q1",
    )
    q2 = st.radio(
        "2. ¿Qué condición garantiza estabilidad en M/M/1?",
        ["λ < μ", "λ = μ", "λ > μ"],
        key="mm1_q2",
    )
    q3 = st.radio(
        "3. ¿Qué representa Wq?",
        ["Tiempo total en el sistema", "Tiempo promedio de espera antes del servicio", "Número promedio en la cola"],
        key="mm1_q3",
    )

    if st.button("Revisar respuestas", key="revisar_mm1"):
        puntaje = 0
        puntaje += q1 == "12 clientes/h"
        puntaje += q2 == "λ < μ"
        puntaje += q3 == "Tiempo promedio de espera antes del servicio"

        if puntaje == 3:
            st.success("3/3 · Excelente. Puedes continuar con la evaluación del módulo.")
        elif puntaje == 2:
            st.info("2/3 · Buen avance. Revisa el concepto que fallaste antes de continuar.")
        else:
            st.warning(f"{puntaje}/3 · Conviene repasar las secciones 3, 4 y 5 antes de avanzar.")

# -----------------------------------------------------------------------------
# Cierre
# -----------------------------------------------------------------------------
st.markdown("---")
st.success("Siguiente paso: ve al módulo 03 para realizar la evaluación interactiva del modelo M/M/1.")
st.caption("Mag. Carlos Alberto Nieto Astahuamán · Investigación de Operaciones · Recurso educativo interactivo")
