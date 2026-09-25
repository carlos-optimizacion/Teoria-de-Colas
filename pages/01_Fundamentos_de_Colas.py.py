import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="01 - Fundamentos | Laboratorio visual",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #F7F9FC; }
    .block-container { padding-top: 1.1rem; padding-bottom: 2.6rem; max-width: 1450px; }
    .hero-learn {
        background: linear-gradient(135deg, #12324D 0%, #1F5A86 58%, #2D7BA8 100%);
        border-radius: 24px; padding: 30px 34px; color: white;
        box-shadow: 0 16px 34px rgba(23,50,77,.16); margin-bottom: 1rem;
    }
    .hero-learn h1 { margin: 0; font-size: 2.15rem; line-height: 1.12; }
    .hero-learn p { margin: .7rem 0 0; opacity: .94; max-width: 1050px; font-size: 1.03rem; }
    .eyebrow { font-size: .76rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; opacity: .82; }
    .learn-card, .concept-card {
        background: white; border: 1px solid #E3E9F0; border-radius: 16px;
        padding: 18px 20px; box-shadow: 0 5px 16px rgba(31,78,120,.05);
    }
    .learn-card { min-height: 132px; }
    .learn-card h4 { margin: 0 0 .45rem; color: #17324D; }
    .learn-card p { margin: 0; color: #5A6675; }
    .concept-card { min-height: 145px; }
    .concept-card .symbol { font-size: 1.5rem; font-weight: 850; color: #1F5A86; }
    .concept-card .label { font-weight: 750; color: #17324D; margin-top: .15rem; }
    .concept-card .desc { color: #667085; font-size: .91rem; margin-top: .35rem; }
    .example-box {
        background: #FFFFFF; border: 1px solid #DDE5EC; border-left: 6px solid #1F5A86;
        border-radius: 16px; padding: 18px 20px; margin: .5rem 0 1rem;
    }
    .warning-box {
        background: #FFF7E6; border: 1px solid #F0D9AB; border-left: 6px solid #D97706;
        border-radius: 14px; padding: 16px 18px; margin: .45rem 0 1rem; color: #75440A;
    }
    .skill-box {
        background: linear-gradient(135deg, #F0F6FB 0%, #FFFFFF 100%);
        border: 1px solid #CDDFEC; border-radius: 18px; padding: 20px 22px; margin: .5rem 0 1rem;
    }
    div[data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E1E7EE; padding: 14px 16px;
        border-radius: 14px; box-shadow: 0 4px 12px rgba(31,78,120,.04);
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_anatomia():
    html = """
    <html><body style="margin:0;background:#F7F9FC;font-family:Arial,sans-serif;">
    <div style="background:#fff;border:1px solid #E1E8EF;border-radius:22px;padding:10px;box-shadow:0 8px 22px rgba(31,78,120,.06);">
    <svg viewBox="0 0 1180 360" width="100%" role="img" aria-label="Anatomía visual de un sistema de colas">
      <defs>
        <linearGradient id="bgBase" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#F8FBFE"/><stop offset="100%" stop-color="#EEF5FA"/>
        </linearGradient>
        <marker id="arrBase" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
          <path d="M0,0 L0,6 L9,3 z" fill="#7B8EA3"/>
        </marker>
      </defs>
      <rect x="8" y="8" width="1164" height="344" rx="22" fill="url(#bgBase)"/>
      <text x="40" y="48" font-size="24" font-weight="700" fill="#17324D">Anatomía de un sistema de espera</text>
      <text x="40" y="75" font-size="14" fill="#667085">Todo modelo de colas intenta representar este flujo básico.</text>

      <rect x="35" y="110" width="210" height="145" rx="18" fill="#fff" stroke="#DCE6EF"/>
      <rect x="285" y="110" width="270" height="145" rx="18" fill="#fff" stroke="#DCE6EF"/>
      <rect x="610" y="95" width="300" height="175" rx="18" fill="#fff" stroke="#DCE6EF"/>
      <rect x="955" y="110" width="190" height="145" rx="18" fill="#fff" stroke="#DCE6EF"/>

      <line x1="245" y1="182" x2="280" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arrBase)"/>
      <line x1="555" y1="182" x2="605" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arrBase)"/>
      <line x1="910" y1="182" x2="950" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arrBase)"/>

      <circle cx="88" cy="145" r="10" fill="#2D6A9F"/><rect x="76" y="158" width="24" height="28" rx="7" fill="#2D6A9F"/>
      <circle cx="130" cy="145" r="10" fill="#2D6A9F"/><rect x="118" y="158" width="24" height="28" rx="7" fill="#2D6A9F"/>
      <circle cx="172" cy="145" r="10" fill="#2D6A9F"/><rect x="160" y="158" width="24" height="28" rx="7" fill="#2D6A9F"/>
      <text x="140" y="218" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Llegadas</text>
      <text x="140" y="240" text-anchor="middle" font-size="12.5" fill="#667085">¿Con qué frecuencia llegan?</text>

      <circle cx="345" cy="148" r="9" fill="#527A9E"/><rect x="334" y="160" width="22" height="26" rx="6" fill="#527A9E"/>
      <circle cx="385" cy="148" r="9" fill="#527A9E"/><rect x="374" y="160" width="22" height="26" rx="6" fill="#527A9E"/>
      <circle cx="425" cy="148" r="9" fill="#527A9E"/><rect x="414" y="160" width="22" height="26" rx="6" fill="#527A9E"/>
      <circle cx="465" cy="148" r="9" fill="#527A9E"/><rect x="454" y="160" width="22" height="26" rx="6" fill="#527A9E"/>
      <text x="420" y="218" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Cola</text>
      <text x="420" y="240" text-anchor="middle" font-size="12.5" fill="#667085">¿Quién espera y en qué orden?</text>

      <rect x="645" y="122" width="105" height="95" rx="14" fill="#EAF7EF" stroke="#B7DDC5"/>
      <rect x="770" y="122" width="105" height="95" rx="14" fill="#EAF7EF" stroke="#B7DDC5"/>
      <circle cx="697" cy="150" r="10" fill="#15803D"/><rect x="685" y="163" width="24" height="28" rx="7" fill="#15803D"/>
      <circle cx="822" cy="150" r="10" fill="#15803D"/><rect x="810" y="163" width="24" height="28" rx="7" fill="#15803D"/>
      <text x="760" y="242" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Servidores</text>
      <text x="760" y="260" text-anchor="middle" font-size="12.5" fill="#667085">¿Cuántos atienden y cuánto tardan?</text>

      <circle cx="1050" cy="157" r="28" fill="#EAF7EF" stroke="#A9D8BA" stroke-width="2"/>
      <path d="M1037 157 L1047 167 L1065 145" fill="none" stroke="#15803D" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
      <text x="1050" y="218" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Salida</text>
      <text x="1050" y="240" text-anchor="middle" font-size="12.5" fill="#667085">Cliente atendido o rechazado</text>

      <rect x="40" y="292" width="1095" height="42" rx="18" fill="#EAF1F7"/>
      <text x="590" y="318" text-anchor="middle" font-size="14" font-weight="700" fill="#1F4E78">La teoría de colas conecta demanda, capacidad, variabilidad, espera y nivel de servicio.</text>
    </svg>
    </div></body></html>
    """
    components.html(html, height=405, scrolling=False)


st.markdown(
    """
    <div class="hero-learn">
        <div class="eyebrow">Modo Aprendizaje · Punto de partida</div>
        <h1>01. Fundamentos de Teoría de Colas</h1>
        <p>
            Antes de usar fórmulas, aprende a mirar un proceso como un sistema de llegadas, espera y capacidad.
            Este módulo construye el lenguaje que utilizarás en todos los laboratorios siguientes.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## 1. ¿Qué aprenderás?")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="learn-card"><h4>👀 Observar</h4><p>Reconocer llegadas, cola, servidores y salida en un proceso real.</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="learn-card"><h4>🧩 Clasificar</h4><p>Entender cómo la notación de Kendall resume el sistema.</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="learn-card"><h4>📐 Medir</h4><p>Distinguir utilización, clientes en cola y tiempos de espera.</p></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="learn-card"><h4>💡 Interpretar</h4><p>Relacionar capacidad y servicio con decisiones operativas.</p></div>', unsafe_allow_html=True)

st.markdown("## 2. Mira primero el proceso")
render_anatomia()

st.markdown(
    """
    Una **cola** aparece cuando la demanda y la capacidad no están perfectamente sincronizadas. Incluso si la capacidad promedio es suficiente,
    la variabilidad puede provocar esperas. Por eso la pregunta no es solo “¿puedo atender a todos?”, sino también “¿cuánto esperan y qué nivel de servicio obtengo?”.
    """
)

st.markdown("## 3. Los elementos de cualquier sistema")
v1, v2, v3, v4 = st.columns(4)
with v1:
    st.markdown('<div class="concept-card"><div class="symbol">λ</div><div class="label">Llegadas</div><div class="desc">Ritmo con el que clientes, piezas o solicitudes entran al sistema.</div></div>', unsafe_allow_html=True)
with v2:
    st.markdown('<div class="concept-card"><div class="symbol">μ</div><div class="label">Servicio</div><div class="desc">Ritmo al que cada recurso puede completar atenciones.</div></div>', unsafe_allow_html=True)
with v3:
    st.markdown('<div class="concept-card"><div class="symbol">s</div><div class="label">Servidores</div><div class="desc">Cantidad de recursos que atienden en paralelo.</div></div>', unsafe_allow_html=True)
with v4:
    st.markdown('<div class="concept-card"><div class="symbol">K</div><div class="label">Capacidad</div><div class="desc">Máximo de clientes que pueden estar dentro del sistema, si existe un límite.</div></div>', unsafe_allow_html=True)

st.markdown("### Indicadores que aparecerán en todos los modelos")
i1, i2, i3, i4 = st.columns(4)
i1.metric("ρ", "Utilización")
i2.metric("Lq", "Clientes en cola")
i3.metric("Wq", "Tiempo en cola")
i4.metric("W", "Tiempo total")
st.caption("ρ describe carga de capacidad; Lq y Wq describen congestión; W incorpora espera más servicio.")

st.markdown("## 4. Aprende a leer la notación de Kendall")
st.markdown(
    """
    La forma general puede escribirse como **A/S/s/K/N/D**. Los tres primeros elementos son los más frecuentes:

    - **A**: patrón de llegadas. M = exponencial/Poisson, D = determinista, G = general.
    - **S**: patrón del tiempo de servicio. M = exponencial, D = determinista, G = general.
    - **s**: número de servidores.
    - **K**: capacidad total del sistema cuando es finita.
    - **N**: población potencial, si es limitada.
    - **D**: disciplina de atención, por ejemplo FIFO o prioridad.
    """
)

st.markdown("## 5. Laboratorio de clasificación")
st.markdown("Configura un sistema y observa qué notación básica describe mejor sus características.")

k1, k2, k3 = st.columns(3)
with k1:
    llegada = st.selectbox("Patrón de llegadas", ["Aleatorio (M)", "Determinista (D)"])
with k2:
    servicio = st.selectbox("Patrón de servicio", ["Aleatorio exponencial (M)", "Determinista (D)", "General (G)"])
with k3:
    servidores = st.slider("Número de servidores", 1, 6, 1)

cap_finita = st.checkbox("El sistema tiene una capacidad total máxima")
K = None
if cap_finita:
    K = st.number_input("Capacidad total K", min_value=servidores, value=max(servidores, 6), step=1)

A = "M" if llegada.startswith("Aleatorio") else "D"
S = "M" if servicio.startswith("Aleatorio") else ("D" if servicio.startswith("Determinista") else "G")
notacion = f"{A}/{S}/{servidores}" + (f"/{int(K)}" if cap_finita else "")

st.success(f"Notación básica sugerida: **{notacion}**")
if not cap_finita:
    st.caption("Al no indicar K, se asume la versión clásica con capacidad de espera no limitada, salvo que el modelo especifique otra cosa.")
else:
    st.caption("K representa la capacidad total: clientes en servicio + clientes esperando.")

st.markdown("## 6. La Ley de Little: una relación transversal")
st.markdown(
    """
    Siempre que el sistema se encuentre en condiciones estables y se utilicen promedios coherentes, la Ley de Little conecta cantidad y tiempo:
    """
)
st.latex(r"L = \lambda W \qquad ; \qquad L_q = \lambda W_q")
st.markdown(
    """
    <div class="example-box">
        <b>Ejemplo intuitivo:</b> si entran 10 clientes por hora y cada cliente permanece, en promedio, 0.2 horas dentro del sistema,
        entonces hay aproximadamente 2 clientes presentes en promedio: <b>L = 10 × 0.2 = 2</b>.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## 7. Reto de destreza: reconoce el modelo")
st.markdown(
    """
    <div class="skill-box">
        <b>Caso:</b> en una clínica las llegadas son aleatorias, los tiempos de atención se consideran exponenciales,
        existen 3 médicos y la sala admite como máximo 12 pacientes entre atención y espera.
    </div>
    """,
    unsafe_allow_html=True,
)

respuesta = st.selectbox("¿Qué notación describe mejor el caso?", ["Selecciona...", "M/M/1", "M/M/3", "M/M/3/12", "D/M/3/12"])
if respuesta == "M/M/3/12":
    st.success("✅ Correcto. Identificaste llegadas M, servicio M, 3 servidores y capacidad total K = 12.")
elif respuesta != "Selecciona...":
    st.warning("Revisa el significado de cada posición: llegadas / servicio / servidores / capacidad total.")

st.markdown("## 8. Qué debes llevarte de este módulo")
st.markdown(
    """
    - Un sistema de colas se entiende observando **demanda, espera y capacidad**.
    - La notación de Kendall resume los supuestos esenciales del sistema.
    - Una cola puede existir incluso cuando la capacidad promedio supera la demanda.
    - Los indicadores ρ, Lq, Wq y W convierten el comportamiento del sistema en información para decidir.
    - La comprensión se fortalece clasificando y experimentando con sistemas, no memorizando definiciones aisladas.
    """
)

st.info("Siguiente paso recomendado: M/M/1, donde analizarás una cola aleatoria con un único servidor y observarás cómo la espera aumenta al acercarse a la capacidad máxima.")
