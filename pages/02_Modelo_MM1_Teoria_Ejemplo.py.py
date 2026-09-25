import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="02 - M/M/1 | Laboratorio interactivo",
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
    .block-container { padding-top: 1.15rem; padding-bottom: 2.8rem; max-width: 1450px; }
    .hero-learn {
        background: linear-gradient(135deg, #12324D 0%, #1F5A86 58%, #2D7BA8 100%);
        border-radius: 24px; padding: 30px 34px; color: white;
        box-shadow: 0 16px 34px rgba(23,50,77,.16); margin-bottom: 1rem;
    }
    .hero-learn h1 { margin: 0; font-size: 2.15rem; line-height: 1.12; }
    .hero-learn p { margin: .7rem 0 0; opacity: .94; max-width: 1050px; font-size: 1.03rem; }
    .eyebrow { font-size: .76rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; opacity: .82; }
    .learn-card, .concept-card, .insight-card {
        background: white; border: 1px solid #E3E9F0; border-radius: 16px;
        padding: 18px 20px; box-shadow: 0 5px 16px rgba(31,78,120,.05);
    }
    .learn-card { min-height: 132px; }
    .learn-card h4 { margin: 0 0 .45rem; color: #17324D; }
    .learn-card p { margin: 0; color: #5A6675; }
    .concept-card { min-height: 145px; }
    .concept-card .symbol { font-size: 1.55rem; font-weight: 850; color: #1F5A86; }
    .concept-card .label { font-weight: 750; color: #17324D; margin-top: .15rem; }
    .concept-card .desc { color: #667085; font-size: .91rem; margin-top: .35rem; }
    .example-box, .decision-box {
        background: #FFFFFF; border: 1px solid #DDE5EC; border-left: 6px solid #1F5A86;
        border-radius: 16px; padding: 18px 20px; margin: .5rem 0 1rem;
    }
    .warning-box {
        background: #FFF7E6; border: 1px solid #F0D9AB; border-left: 6px solid #D97706;
        border-radius: 14px; padding: 16px 18px; margin: .45rem 0 1rem; color: #75440A;
    }
    .critical-box {
        background: #FDECEC; border: 1px solid #F2C7C7; border-left: 6px solid #B42318;
        border-radius: 14px; padding: 16px 18px; margin: .45rem 0 1rem; color: #8A1C15;
    }
    .success-box {
        background: #EAF7EF; border: 1px solid #C8E4D1; border-left: 6px solid #15803D;
        border-radius: 14px; padding: 16px 18px; margin: .45rem 0 1rem; color: #14532D;
    }
    .skill-box {
        background: linear-gradient(135deg, #F0F6FB 0%, #FFFFFF 100%);
        border: 1px solid #CDDFEC; border-radius: 18px; padding: 20px 22px; margin: .5rem 0 1rem;
    }
    .formula-note { color: #667085; font-size: .9rem; }
    div[data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E1E7EE; padding: 14px 16px;
        border-radius: 14px; box-shadow: 0 4px 12px rgba(31,78,120,.04);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #FFFFFF; border: 1px solid #E1E7EE; border-radius: 10px 10px 0 0;
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
def calcular_mm1(t_llegada_min: float, t_atencion_min: float):
    lam = 60.0 / t_llegada_min
    mu = 60.0 / t_atencion_min
    rho = lam / mu

    if rho >= 1:
        return {
            "estable": False,
            "lambda": lam,
            "mu": mu,
            "rho": rho,
            "L": float("inf"),
            "Lq": float("inf"),
            "W": float("inf"),
            "Wq": float("inf"),
            "P_espera": 1.0,
        }

    L = rho / (1 - rho)
    Lq = rho**2 / (1 - rho)
    W = 1 / (mu - lam)
    Wq = lam / (mu * (mu - lam))

    return {
        "estable": True,
        "lambda": lam,
        "mu": mu,
        "rho": rho,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "P_espera": rho,
    }


def persona_svg(x, y, escala=1.0, color="#2D6A9F", opacity=1.0):
    r = 9 * escala
    body_w = 22 * escala
    body_h = 24 * escala
    return f"""
    <g opacity="{opacity}">
        <circle cx="{x}" cy="{y}" r="{r}" fill="{color}" />
        <rect x="{x-body_w/2}" y="{y+r+3}" width="{body_w}" height="{body_h}" rx="{6*escala}" fill="{color}" />
    </g>
    """


def render_sistema_mm1(resultado, titulo="Sistema M/M/1"):
    estable = resultado["estable"]
    rho_pct = resultado["rho"] * 100
    lq = resultado["Lq"] if estable else float("inf")
    p_espera = resultado["P_espera"] * 100

    if estable:
        personas_visibles = max(1, min(5, int(math.ceil(lq)))) if lq > 0.05 else 1
        estado = "Sistema estable"
        estado_color = "#15803D"
        estado_bg = "#EAF7EF"
        lq_text = f"{lq:.2f} clientes en cola (promedio)"
    else:
        personas_visibles = 5
        estado = "Capacidad insuficiente"
        estado_color = "#B42318"
        estado_bg = "#FDECEC"
        lq_text = "La cola crece sin límite en el modelo"

    cola_svg = ""
    posiciones = [385, 425, 465, 505, 545]
    for i, x in enumerate(posiciones[:personas_visibles]):
        op = 1.0 if i < 3 else 0.72
        cola_svg += persona_svg(x, 145, 0.78, "#527A9E", op)

    svg = f"""
    <div style="background:#fff;border:1px solid #E1E8EF;border-radius:22px;padding:14px 16px 8px;box-shadow:0 8px 22px rgba(31,78,120,.06);margin:.4rem 0 1rem;overflow-x:auto;">
    <svg viewBox="0 0 1180 360" width="100%" role="img" aria-label="Diagrama visual de un sistema de colas M/M/1">
        <defs>
            <linearGradient id="bgMM1" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#F7FAFD"/>
                <stop offset="100%" stop-color="#EEF5FA"/>
            </linearGradient>
            <linearGradient id="srvMM1" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#DDF3E6"/>
                <stop offset="100%" stop-color="#C7E9D4"/>
            </linearGradient>
            <filter id="shadowMM1" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#17324D" flood-opacity="0.10"/>
            </filter>
            <marker id="arrowMM1" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
                <path d="M0,0 L0,6 L9,3 z" fill="#7B8EA3"/>
            </marker>
        </defs>

        <rect x="8" y="8" width="1164" height="344" rx="22" fill="url(#bgMM1)"/>
        <text x="40" y="48" font-size="24" font-family="Arial, sans-serif" font-weight="700" fill="#17324D">{titulo}</text>
        <text x="40" y="75" font-size="14" font-family="Arial, sans-serif" fill="#667085">Un flujo de llegadas, una sola cola y un único servidor.</text>

        <!-- Zonas -->
        <rect x="40" y="105" width="220" height="150" rx="18" fill="#FFFFFF" stroke="#DCE6EF" filter="url(#shadowMM1)"/>
        <rect x="300" y="105" width="300" height="150" rx="18" fill="#FFFFFF" stroke="#DCE6EF" filter="url(#shadowMM1)"/>
        <rect x="645" y="105" width="235" height="150" rx="18" fill="url(#srvMM1)" stroke="#B7DDC5" filter="url(#shadowMM1)"/>
        <rect x="925" y="105" width="210" height="150" rx="18" fill="#FFFFFF" stroke="#DCE6EF" filter="url(#shadowMM1)"/>

        <!-- Flechas -->
        <line x1="260" y1="180" x2="295" y2="180" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arrowMM1)"/>
        <line x1="600" y1="180" x2="640" y2="180" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arrowMM1)"/>
        <line x1="880" y1="180" x2="920" y2="180" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arrowMM1)"/>

        <!-- Llegadas -->
        {persona_svg(92, 138, 0.72, '#2D6A9F')}
        {persona_svg(135, 138, 0.72, '#2D6A9F')}
        {persona_svg(178, 138, 0.72, '#2D6A9F')}
        <text x="150" y="212" text-anchor="middle" font-size="17" font-family="Arial, sans-serif" font-weight="700" fill="#17324D">Llegadas</text>
        <text x="150" y="235" text-anchor="middle" font-size="13" font-family="Arial, sans-serif" fill="#667085">λ = {resultado['lambda']:.2f} clientes/h</text>

        <!-- Cola -->
        {cola_svg}
        <line x1="345" y1="190" x2="558" y2="190" stroke="#D7E1EA" stroke-width="3" stroke-dasharray="7 7"/>
        <text x="450" y="220" text-anchor="middle" font-size="17" font-family="Arial, sans-serif" font-weight="700" fill="#17324D">Cola de espera</text>
        <text x="450" y="242" text-anchor="middle" font-size="13" font-family="Arial, sans-serif" fill="#667085">{lq_text}</text>

        <!-- Servidor -->
        {persona_svg(760, 134, 0.82, '#15803D')}
        <rect x="705" y="182" width="110" height="14" rx="7" fill="#6E8F7B"/>
        <rect x="728" y="196" width="12" height="32" rx="5" fill="#6E8F7B"/>
        <rect x="780" y="196" width="12" height="32" rx="5" fill="#6E8F7B"/>
        <text x="762" y="220" text-anchor="middle" font-size="17" font-family="Arial, sans-serif" font-weight="700" fill="#14532D">1 servidor</text>
        <text x="762" y="242" text-anchor="middle" font-size="13" font-family="Arial, sans-serif" fill="#3F6B4F">μ = {resultado['mu']:.2f} clientes/h</text>

        <!-- Salida -->
        <circle cx="1030" cy="158" r="28" fill="#EAF7EF" stroke="#A9D8BA" stroke-width="2"/>
        <path d="M1017 158 L1027 168 L1045 146" fill="none" stroke="#15803D" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        <text x="1030" y="212" text-anchor="middle" font-size="17" font-family="Arial, sans-serif" font-weight="700" fill="#17324D">Salida</text>
        <text x="1030" y="235" text-anchor="middle" font-size="13" font-family="Arial, sans-serif" fill="#667085">Cliente atendido</text>

        <!-- Pie de estado -->
        <rect x="40" y="285" width="250" height="44" rx="22" fill="{estado_bg}"/>
        <circle cx="65" cy="307" r="7" fill="{estado_color}"/>
        <text x="84" y="313" font-size="14" font-family="Arial, sans-serif" font-weight="700" fill="{estado_color}">{estado}</text>

        <text x="360" y="313" font-size="14" font-family="Arial, sans-serif" fill="#5B6675">Utilización:</text>
        <text x="445" y="313" font-size="14" font-family="Arial, sans-serif" font-weight="700" fill="#17324D">{rho_pct:.1f}%</text>
        <text x="555" y="313" font-size="14" font-family="Arial, sans-serif" fill="#5B6675">Prob. de esperar:</text>
        <text x="675" y="313" font-size="14" font-family="Arial, sans-serif" font-weight="700" fill="#17324D">{p_espera:.1f}%</text>
        <text x="790" y="313" font-size="14" font-family="Arial, sans-serif" fill="#5B6675">Servidor:</text>
        <text x="855" y="313" font-size="14" font-family="Arial, sans-serif" font-weight="700" fill="#17324D">1 estación</text>
    </svg>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)


def grafico_sensibilidad(mu, rho_actual=None):
    rhos = [i / 100 for i in range(10, 98, 2)]
    datos = []
    for r in rhos:
        lam = r * mu
        wq_h = lam / (mu * (mu - lam))
        datos.append({"Utilización": r * 100, "Wq": wq_h * 60})

    df = pd.DataFrame(datos)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Utilización"],
            y=df["Wq"],
            mode="lines",
            name="Espera promedio",
            line=dict(width=4),
            hovertemplate="Utilización: %{x:.0f}%<br>Espera: %{y:.1f} min<extra></extra>",
        )
    )
    if rho_actual is not None and rho_actual < 1:
        lam_actual = rho_actual * mu
        wq_actual = lam_actual / (mu * (mu - lam_actual)) * 60
        fig.add_trace(
            go.Scatter(
                x=[rho_actual * 100],
                y=[wq_actual],
                mode="markers+text",
                text=["Escenario actual"],
                textposition="top center",
                name="Escenario actual",
                marker=dict(size=13),
                hovertemplate="Actual: %{x:.1f}%<br>Espera: %{y:.1f} min<extra></extra>",
            )
        )
    fig.update_layout(
        title="Cómo crece la espera cuando el servidor se acerca a su capacidad",
        xaxis_title="Utilización del servidor (%)",
        yaxis_title="Espera promedio en cola (min)",
        template="plotly_white",
        height=430,
        margin=dict(l=30, r=20, t=70, b=40),
        legend=dict(orientation="h", y=1.08, x=0),
    )
    fig.update_xaxes(range=[8, 100])
    return fig


# -----------------------------------------------------------------------------
# Encabezado
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-learn">
        <div class="eyebrow">Modo Aprendizaje · Laboratorio de Teoría de Colas</div>
        <h1>02. Modelo M/M/1</h1>
        <p>
            Aprende el modelo observando el sistema, resolviendo un ejemplo y modificando sus condiciones.
            El objetivo no es memorizar fórmulas, sino comprender qué provoca la cola y cómo cambia la experiencia del cliente.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 1. Qué aprenderás
# -----------------------------------------------------------------------------
st.markdown("## 1. ¿Qué aprenderás?")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="learn-card"><h4>🔎 Reconocer</h4><p>Identificar cuándo un proceso corresponde a una cola con un único servidor.</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="learn-card"><h4>👀 Visualizar</h4><p>Entender dónde llegan los clientes, dónde esperan y cómo funciona la estación de servicio.</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="learn-card"><h4>🧪 Experimentar</h4><p>Cambiar ritmos de llegada y atención para observar cómo se comporta la cola.</p></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="learn-card"><h4>💡 Decidir</h4><p>Interpretar utilización y espera para reconocer cuándo la operación necesita una mejora.</p></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Historia visual
# -----------------------------------------------------------------------------
st.markdown("## 2. Mira el sistema antes de usar fórmulas")
st.markdown(
    """
    Imagina una **ventanilla con un solo trabajador**. Los clientes llegan de forma aleatoria, esperan en una sola fila
    y pasan uno por uno al puesto de atención. Esa situación puede representarse con un modelo **M/M/1**.
    """
)

ejemplo_visual = calcular_mm1(6.0, 4.0)
render_sistema_mm1(ejemplo_visual, "Ejemplo visual · ventanilla de atención")

st.markdown(
    """
    La notación **M/M/1** resume tres características:

    - **Primer M:** los tiempos entre llegadas son aleatorios y se modelan con distribución exponencial; el número de llegadas por intervalo es compatible con Poisson.
    - **Segundo M:** los tiempos de atención también son aleatorios y exponenciales.
    - **1:** existe un solo servidor atendiendo.

    En el modelo clásico se considera una cola FIFO, población potencial grande y capacidad de espera no limitada.
    """
)

# -----------------------------------------------------------------------------
# 3. Variables
# -----------------------------------------------------------------------------
st.markdown("## 3. Las cuatro ideas que debes dominar")
v1, v2, v3, v4 = st.columns(4)
with v1:
    st.markdown('<div class="concept-card"><div class="symbol">λ</div><div class="label">Ritmo de llegada</div><div class="desc">Cuántos clientes llegan por hora. Si llegan cada vez más rápido, λ aumenta.</div></div>', unsafe_allow_html=True)
with v2:
    st.markdown('<div class="concept-card"><div class="symbol">μ</div><div class="label">Ritmo de atención</div><div class="desc">Cuántos clientes puede completar el servidor por hora. Una atención más rápida eleva μ.</div></div>', unsafe_allow_html=True)
with v3:
    st.markdown('<div class="concept-card"><div class="symbol">ρ</div><div class="label">Utilización</div><div class="desc">Porcentaje del tiempo en que el servidor se encuentra ocupado.</div></div>', unsafe_allow_html=True)
with v4:
    st.markdown('<div class="concept-card"><div class="symbol">Wq</div><div class="label">Espera en cola</div><div class="desc">Tiempo que el cliente espera antes de iniciar su atención.</div></div>', unsafe_allow_html=True)

st.markdown("### Del dato observado a la tasa")
st.markdown(
    """
    En una operación real normalmente medimos **minutos**, por eso primero convertimos los tiempos observados:
    """
)
cc1, cc2 = st.columns(2)
with cc1:
    st.latex(r"\lambda = \frac{60}{\text{minutos entre llegadas}}")
    st.caption("Ejemplo: una llegada cada 6 min → λ = 10 clientes/h.")
with cc2:
    st.latex(r"\mu = \frac{60}{\text{minutos por atención}}")
    st.caption("Ejemplo: una atención de 4 min → μ = 15 clientes/h.")

# -----------------------------------------------------------------------------
# 4. Estabilidad
# -----------------------------------------------------------------------------
st.markdown("## 4. La primera pregunta siempre es: ¿la capacidad alcanza?")
st.latex(r"\rho = \frac{\lambda}{\mu}")
st.latex(r"\lambda < \mu \quad \Longleftrightarrow \quad \rho < 1")

st.markdown(
    """
    <div class="warning-box">
        <b>Idea clave:</b> un sistema estable también puede tener cola. Cuando λ &lt; μ, el servidor tiene capacidad promedio suficiente,
        pero la variabilidad de las llegadas y de los tiempos de atención puede generar espera. Cuando λ ≥ μ, la capacidad promedio ya no alcanza
        y la cola tiende a crecer sin límite dentro del modelo M/M/1 clásico.
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 5. Fórmulas
# -----------------------------------------------------------------------------
st.markdown("## 5. Ahora sí: las fórmulas esenciales")
with st.expander("Ver fórmulas y qué significa cada resultado", expanded=False):
    f1, f2 = st.columns(2)
    with f1:
        st.markdown("**Cantidad de clientes**")
        st.latex(r"L = \frac{\rho}{1-\rho}")
        st.latex(r"L_q = \frac{\rho^2}{1-\rho}")
        st.markdown('<div class="formula-note"><b>L</b> = clientes promedio en todo el sistema. <b>Lq</b> = clientes promedio esperando.</div>', unsafe_allow_html=True)
    with f2:
        st.markdown("**Tiempos**")
        st.latex(r"W = \frac{1}{\mu-\lambda}")
        st.latex(r"W_q = \frac{\lambda}{\mu(\mu-\lambda)}")
        st.markdown('<div class="formula-note"><b>W</b> = espera + atención. <b>Wq</b> = solo la espera antes de ser atendido.</div>', unsafe_allow_html=True)
    st.markdown("**Ley de Little**")
    st.latex(r"L = \lambda W \qquad ; \qquad L_q = \lambda W_q")

# -----------------------------------------------------------------------------
# 6. Ejemplo guiado
# -----------------------------------------------------------------------------
st.markdown("## 6. Ejemplo guiado: ventanilla de atención")
st.markdown(
    """
    <div class="example-box">
        <b>Situación:</b> llega un cliente cada <b>6 minutos</b>, la atención tarda <b>4 minutos</b> y existe <b>un solo trabajador</b>.
        Queremos saber si la estación tiene capacidad suficiente y qué experiencia enfrenta el cliente.
    </div>
    """,
    unsafe_allow_html=True,
)

r_e = calcular_mm1(6.0, 4.0)
paso1, paso2, paso3 = st.tabs(["1 · Convertir los datos", "2 · Obtener resultados", "3 · Leer la operación"])

with paso1:
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("**Llegadas**")
        st.latex(r"\lambda = \frac{60}{6}=10\ clientes/h")
    with p2:
        st.markdown("**Atención**")
        st.latex(r"\mu = \frac{60}{4}=15\ clientes/h")
    with p3:
        st.markdown("**Utilización**")
        st.latex(r"\rho = \frac{10}{15}=0.667")
    st.success("10 < 15: la capacidad promedio es suficiente y el sistema es estable.")

with paso2:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Utilización", f"{r_e['rho']*100:.1f}%")
    m2.metric("Prob. de esperar", f"{r_e['P_espera']*100:.1f}%")
    m3.metric("Clientes en cola", f"{r_e['Lq']:.2f}")
    m4.metric("Espera Wq", f"{r_e['Wq']*60:.1f} min")
    m5.metric("Tiempo total W", f"{r_e['W']*60:.1f} min")

    with st.expander("Ver la sustitución matemática"):
        st.latex(r"L_q=\frac{0.667^2}{1-0.667}\approx1.33")
        st.latex(r"W_q=\frac{10}{15(15-10)}=0.1333\ h\approx8\ min")
        st.latex(r"W=\frac{1}{15-10}=0.20\ h=12\ min")

with paso3:
    st.markdown(
        """
        <div class="success-box">
            <b>Interpretación:</b> el trabajador está ocupado aproximadamente el <b>66.7 %</b> del tiempo. Aunque la capacidad promedio supera la demanda,
            un cliente tiene alrededor de <b>66.7 % de probabilidad de encontrar ocupado al servidor</b>. En promedio espera <b>8 minutos</b>
            antes de ser atendido y permanece aproximadamente <b>12 minutos</b> en todo el sistema.
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# 7. Laboratorio interactivo
# -----------------------------------------------------------------------------
st.markdown("## 7. Laboratorio interactivo: cambia el sistema y observa la cola")
st.markdown(
    """
    Aquí se valida la comprensión **experimentando**. Modifica los tiempos y observa cómo cambian la utilización,
    la probabilidad de esperar y el tiempo de cola. No necesitas memorizar una respuesta fija.
    """
)

lab1, lab2 = st.columns([1, 1])
with lab1:
    t_llegada = st.slider("Llega 1 cliente cada... (min)", 1.0, 15.0, 6.0, 0.5)
with lab2:
    t_atencion = st.slider("Cada atención tarda... (min)", 1.0, 15.0, 4.0, 0.5)

r_lab = calcular_mm1(t_llegada, t_atencion)
render_sistema_mm1(r_lab, "Tu escenario interactivo")

if not r_lab["estable"]:
    st.markdown(
        f"""
        <div class="critical-box">
            <b>⚠️ Sistema inestable.</b> Llega un cliente cada <b>{t_llegada:.1f} min</b>, pero atenderlo tarda <b>{t_atencion:.1f} min</b>.
            Con un solo servidor, la demanda promedio iguala o supera la capacidad. En el modelo M/M/1 la cola crecerá sin límite.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    l1, l2, l3, l4, l5 = st.columns(5)
    l1.metric("Utilización", f"{r_lab['rho']*100:.1f}%")
    l2.metric("Prob. de esperar", f"{r_lab['P_espera']*100:.1f}%")
    l3.metric("Cola promedio", f"{r_lab['Lq']:.2f}")
    l4.metric("Espera promedio", f"{r_lab['Wq']*60:.1f} min")
    l5.metric("Tiempo total", f"{r_lab['W']*60:.1f} min")

    if r_lab["rho"] >= 0.90:
        st.warning("La capacidad aún es suficiente, pero el sistema trabaja muy cerca de su límite y pequeñas variaciones pueden elevar fuertemente la espera.")
    else:
        st.success("El sistema es estable. Ahora prueba acercar los tiempos de llegada y atención para observar cómo se amplifica la espera.")

st.plotly_chart(grafico_sensibilidad(r_lab["mu"], r_lab["rho"] if r_lab["estable"] else None), use_container_width=True)
st.caption("El gráfico mantiene constante la velocidad de atención del escenario y muestra por qué la espera se dispara cuando la utilización se aproxima al 100 %.")

# -----------------------------------------------------------------------------
# 8. Reto de destreza
# -----------------------------------------------------------------------------
st.markdown("## 8. Reto de destreza: logra el nivel de servicio")
st.markdown(
    """
    <div class="skill-box">
        <b>Reto:</b> los clientes llegan cada <b>6 minutos</b>. Ajusta únicamente el tiempo promedio de atención hasta conseguir
        una <b>espera promedio de 5 minutos o menos</b> sin volver inestable el sistema.
        La validación se realiza con el comportamiento del modelo, no con una pregunta de memoria.
    </div>
    """,
    unsafe_allow_html=True,
)

reto_atencion = st.slider("Ajusta el tiempo de atención del reto (min)", 1.0, 7.0, 4.5, 0.1, key="reto_mm1")
r_reto = calcular_mm1(6.0, reto_atencion)

if not r_reto["estable"]:
    st.error("Todavía no funciona: con ese tiempo de atención la capacidad del servidor no supera el ritmo de llegada.")
else:
    rr1, rr2, rr3 = st.columns(3)
    rr1.metric("Utilización", f"{r_reto['rho']*100:.1f}%")
    rr2.metric("Prob. de esperar", f"{r_reto['P_espera']*100:.1f}%")
    rr3.metric("Espera Wq", f"{r_reto['Wq']*60:.2f} min")

    if r_reto["Wq"] * 60 <= 5:
        st.success("✅ Reto logrado. Encontraste una configuración estable que cumple la meta de espera. Observa qué ocurrió con la utilización al acelerar la atención.")
    else:
        st.warning("Aún no se cumple la meta de 5 minutos. Reduce el tiempo de atención y observa cómo responde la cola.")

# -----------------------------------------------------------------------------
# 9. Cierre
# -----------------------------------------------------------------------------
st.markdown("## 9. Qué debes llevarte de este módulo")
st.markdown(
    """
    - Una cola puede existir incluso cuando la capacidad promedio es suficiente.
    - En M/M/1, la estabilidad exige **λ < μ**.
    - La espera no crece de forma lineal: aumenta con rapidez cuando la utilización se acerca al 100 %.
    - **Lq** y **Wq** describen la experiencia de espera; **ρ** describe el uso del recurso.
    - La comprensión se demuestra modificando el sistema y explicando su comportamiento, no memorizando una respuesta.
    """
)

st.info("Siguiente paso recomendado: estudiar M/M/s para analizar qué cambia cuando una misma cola es atendida por varios servidores.")
