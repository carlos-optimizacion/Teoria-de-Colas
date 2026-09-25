import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from interpretation_core import marginal_mms_markdown
from interpretation_core import interpret_mms, to_markdown
import streamlit.components.v1 as components

st.set_page_config(
    page_title="04 - M/M/s | Laboratorio interactivo",
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
    .concept-card .symbol { font-size: 1.55rem; font-weight: 850; color: #1F5A86; }
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
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def calcular_mms(t_llegada_min: float, t_atencion_min: float, servidores: int):
    lam = 60.0 / t_llegada_min
    mu = 60.0 / t_atencion_min
    s = int(servidores)
    rho = lam / (s * mu)

    if rho >= 1:
        return {
            "estable": False,
            "lambda": lam,
            "mu": mu,
            "s": s,
            "rho": rho,
            "P0": 0.0,
            "P_espera": 1.0,
            "Lq": float("inf"),
            "L": float("inf"),
            "Wq": float("inf"),
            "W": float("inf"),
        }

    a = lam / mu
    termino = 1.0
    suma = 1.0
    for n in range(1, s):
        termino *= a / n
        suma += termino

    termino_s = termino * a / s
    erlang_c = termino_s / (1 - rho)
    p0 = 1.0 / (suma + erlang_c)
    p_espera = erlang_c * p0
    lq = p_espera * rho / (1 - rho)
    wq = lq / lam
    w = wq + 1 / mu
    l = lam * w

    return {
        "estable": True,
        "lambda": lam,
        "mu": mu,
        "s": s,
        "rho": rho,
        "P0": p0,
        "P_espera": p_espera,
        "Lq": lq,
        "L": l,
        "Wq": wq,
        "W": w,
    }


def persona_svg(x, y, escala=1.0, color="#2D6A9F", opacity=1.0):
    r = 8.5 * escala
    body_w = 21 * escala
    body_h = 23 * escala
    return f"""
    <g opacity="{opacity}">
        <circle cx="{x}" cy="{y}" r="{r}" fill="{color}" />
        <rect x="{x-body_w/2}" y="{y+r+3}" width="{body_w}" height="{body_h}" rx="{6*escala}" fill="{color}" />
    </g>
    """


def render_sistema_mms(resultado, titulo="Sistema M/M/s"):
    estable = resultado["estable"]
    s = resultado["s"]
    rho_pct = resultado["rho"] * 100
    p_espera = resultado["P_espera"] * 100

    if estable:
        lq = resultado["Lq"]
        personas_cola = max(1, min(5, int(math.ceil(lq)))) if lq > 0.05 else 1
        estado = "Capacidad suficiente"
        estado_color = "#15803D"
        estado_bg = "#EAF7EF"
        cola_text = f"{lq:.2f} clientes en cola"
        wq_text = f"{resultado['Wq']*60:.1f} min de espera"
    else:
        personas_cola = 5
        estado = "Capacidad insuficiente"
        estado_color = "#B42318"
        estado_bg = "#FDECEC"
        cola_text = "La cola crece sin límite"
        wq_text = "Se requiere más capacidad"

    cola_svg = "".join(persona_svg(x, 150, 0.72, "#527A9E", 1 if i < 3 else .7)
                       for i, x in enumerate([335, 375, 415, 455, 495][:personas_cola]))

    # Se muestran hasta 5 servidores para mantener legibilidad; si hay más, se indica el total.
    n_vis = min(s, 5)
    base_y = 108
    server_svg = ""
    if n_vis == 1:
        ys = [170]
    else:
        paso = 112 / max(1, n_vis - 1)
        ys = [base_y + i * paso for i in range(n_vis)]

    for i, y in enumerate(ys, start=1):
        server_svg += f"""
        <rect x="675" y="{y-28}" width="185" height="50" rx="14" fill="#EAF7EF" stroke="#B7DDC5" />
        {persona_svg(706, y-8, .55, '#15803D')}
        <text x="748" y="{y-5}" font-size="14" font-family="Arial, sans-serif" font-weight="700" fill="#14532D">Servidor {i}</text>
        <text x="748" y="{y+13}" font-size="11.5" font-family="Arial, sans-serif" fill="#3F6B4F">μ = {resultado['mu']:.2f}/h</text>
        """

    extra = "" if s <= 5 else f"+ {s-5} servidores adicionales"

    html = f"""
    <html><body style="margin:0;background:#F7F9FC;font-family:Arial,sans-serif;">
    <div style="background:#fff;border:1px solid #E1E8EF;border-radius:22px;padding:10px;box-shadow:0 8px 22px rgba(31,78,120,.06);">
    <svg viewBox="0 0 1180 380" width="100%" role="img" aria-label="Diagrama visual de un sistema M/M/s">
        <defs>
            <linearGradient id="bgMMS" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#F7FAFD"/><stop offset="100%" stop-color="#EEF5FA"/>
            </linearGradient>
            <marker id="arrowMMS" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="#7B8EA3"/>
            </marker>
        </defs>
        <rect x="8" y="8" width="1164" height="364" rx="22" fill="url(#bgMMS)"/>
        <text x="40" y="48" font-size="24" font-weight="700" fill="#17324D">{titulo}</text>
        <text x="40" y="74" font-size="14" fill="#667085">Una sola cola alimenta a varios servidores equivalentes en paralelo.</text>

        <rect x="40" y="105" width="205" height="155" rx="18" fill="#FFFFFF" stroke="#DCE6EF"/>
        <rect x="280" y="105" width="260" height="155" rx="18" fill="#FFFFFF" stroke="#DCE6EF"/>
        <rect x="625" y="88" width="285" height="190" rx="18" fill="#FFFFFF" stroke="#DCE6EF"/>
        <rect x="955" y="105" width="185" height="155" rx="18" fill="#FFFFFF" stroke="#DCE6EF"/>

        <line x1="245" y1="182" x2="275" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arrowMMS)"/>
        <line x1="540" y1="182" x2="620" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arrowMMS)"/>
        <line x1="910" y1="182" x2="950" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arrowMMS)"/>

        {persona_svg(88, 142, .7, '#2D6A9F')}
        {persona_svg(128, 142, .7, '#2D6A9F')}
        {persona_svg(168, 142, .7, '#2D6A9F')}
        <text x="142" y="218" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Llegadas</text>
        <text x="142" y="240" text-anchor="middle" font-size="13" fill="#667085">λ = {resultado['lambda']:.2f} clientes/h</text>

        {cola_svg}
        <text x="410" y="218" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Cola única</text>
        <text x="410" y="239" text-anchor="middle" font-size="12.5" fill="#667085">{cola_text}</text>
        <text x="410" y="255" text-anchor="middle" font-size="12.5" fill="#667085">{wq_text}</text>

        {server_svg}
        <text x="767" y="298" text-anchor="middle" font-size="14" font-weight="700" fill="#17324D">{s} servidor(es) en paralelo</text>
        <text x="767" y="317" text-anchor="middle" font-size="12" fill="#667085">{extra}</text>

        <circle cx="1048" cy="156" r="28" fill="#EAF7EF" stroke="#A9D8BA" stroke-width="2"/>
        <path d="M1035 156 L1045 166 L1063 144" fill="none" stroke="#15803D" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        <text x="1048" y="218" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Salida</text>
        <text x="1048" y="240" text-anchor="middle" font-size="13" fill="#667085">Cliente atendido</text>

        <rect x="40" y="310" width="250" height="42" rx="21" fill="{estado_bg}"/>
        <circle cx="65" cy="331" r="7" fill="{estado_color}"/>
        <text x="84" y="336" font-size="14" font-weight="700" fill="{estado_color}">{estado}</text>
        <text x="350" y="336" font-size="14" fill="#5B6675">Utilización por servidor:</text>
        <text x="505" y="336" font-size="14" font-weight="700" fill="#17324D">{rho_pct:.1f}%</text>
        <text x="610" y="336" font-size="14" fill="#5B6675">Prob. de esperar:</text>
        <text x="730" y="336" font-size="14" font-weight="700" fill="#17324D">{p_espera:.1f}%</text>
    </svg>
    </div></body></html>
    """
    components.html(html, height=420, scrolling=False)


def grafico_operadores(t_llegada, t_atencion, max_s=8, actual=None):
    filas = []
    for s in range(1, max_s + 1):
        r = calcular_mms(t_llegada, t_atencion, s)
        if r["estable"]:
            filas.append({"Operadores": s, "Espera": r["Wq"] * 60})
        else:
            filas.append({"Operadores": s, "Espera": None})

    df = pd.DataFrame(filas)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Operadores"], y=df["Espera"], mode="lines+markers",
        name="Espera promedio", line=dict(width=4), marker=dict(size=9),
        hovertemplate="Operadores: %{x}<br>Espera: %{y:.1f} min<extra></extra>"
    ))
    if actual is not None:
        fig.add_vline(x=actual, line_dash="dash", annotation_text="Configuración actual")
    fig.update_layout(
        title="Qué ocurre con la espera cuando agregamos servidores",
        xaxis_title="Número de servidores",
        yaxis_title="Espera promedio en cola (min)",
        template="plotly_white",
        height=420,
        margin=dict(l=30, r=20, t=70, b=40),
        showlegend=False,
    )
    fig.update_xaxes(dtick=1)
    return fig


st.markdown(
    """
    <div class="hero-learn">
        <div class="eyebrow">Modo Aprendizaje · Laboratorio de Teoría de Colas</div>
        <h1>04. Modelo M/M/s</h1>
        <p>
            Aprende qué cambia cuando una sola cola es atendida por varios servidores. El objetivo es comprender
            cómo la capacidad conjunta reduce la congestión y cómo elegir una cantidad razonable de operadores.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## 1. ¿Qué aprenderás?")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="learn-card"><h4>🔎 Reconocer</h4><p>Identificar sistemas con una sola cola y varios servidores equivalentes.</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="learn-card"><h4>👥 Dimensionar</h4><p>Relacionar demanda, tiempo de atención y cantidad de servidores.</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="learn-card"><h4>🧪 Experimentar</h4><p>Agregar o retirar servidores y observar cómo cambia la espera.</p></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="learn-card"><h4>💡 Decidir</h4><p>Interpretar cuándo más capacidad realmente mejora el servicio.</p></div>', unsafe_allow_html=True)

st.markdown("## 2. Primero visualiza el sistema")
st.markdown(
    """
    Piensa en un banco o centro de atención donde todos los clientes forman **una sola fila** y son enviados al siguiente
    operador disponible. Esa estructura es distinta a tener filas independientes: aquí los servidores comparten la misma demanda.
    """
)

r_visual = calcular_mms(10.0, 15.0, 2)
render_sistema_mms(r_visual, "Ejemplo visual · dos servidores compartiendo una cola")

st.markdown(
    """
    En **M/M/s**, el primer M representa llegadas aleatorias, el segundo M representa tiempos de servicio exponenciales y **s** indica
    cuántos servidores trabajan en paralelo. En la versión clásica se supone una cola FIFO, servidores equivalentes y capacidad de espera no limitada.
    """
)

st.markdown("## 3. Las variables que importan")
v1, v2, v3, v4 = st.columns(4)
with v1:
    st.markdown('<div class="concept-card"><div class="symbol">λ</div><div class="label">Llegadas</div><div class="desc">Clientes que llegan por hora al sistema completo.</div></div>', unsafe_allow_html=True)
with v2:
    st.markdown('<div class="concept-card"><div class="symbol">μ</div><div class="label">Servicio individual</div><div class="desc">Clientes por hora que puede atender cada servidor.</div></div>', unsafe_allow_html=True)
with v3:
    st.markdown('<div class="concept-card"><div class="symbol">s</div><div class="label">Servidores</div><div class="desc">Cantidad de operadores equivalentes disponibles en paralelo.</div></div>', unsafe_allow_html=True)
with v4:
    st.markdown('<div class="concept-card"><div class="symbol">ρ</div><div class="label">Utilización</div><div class="desc">Carga promedio por servidor respecto de la capacidad conjunta.</div></div>', unsafe_allow_html=True)

st.markdown("### La capacidad se evalúa de forma conjunta")
st.latex(r"\rho = \frac{\lambda}{s\mu}")
st.markdown(
    """
    <div class="warning-box">
        <b>Idea clave:</b> un servidor individual puede ser más lento que el ritmo de llegada y aun así el sistema completo ser estable.
        Lo importante es que la capacidad agregada <b>s × μ</b> sea mayor que λ. Si ρ ≥ 1, la cola tenderá a crecer sin límite.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Ver fórmulas principales", expanded=False):
    st.latex(r"P_0 = \left[\sum_{n=0}^{s-1}\frac{(\lambda/\mu)^n}{n!}+\frac{(\lambda/\mu)^s}{s!(1-\rho)}\right]^{-1}")
    st.latex(r"P(\text{espera})=\frac{(\lambda/\mu)^s}{s!(1-\rho)}P_0")
    st.latex(r"L_q=P(\text{espera})\frac{\rho}{1-\rho}")
    st.latex(r"W_q=\frac{L_q}{\lambda}\qquad ; \qquad W=W_q+\frac{1}{\mu}")
    st.markdown('<div class="formula-note">Estas expresiones corresponden al modelo clásico M/M/s con cola infinita y servidores equivalentes.</div>', unsafe_allow_html=True)

st.markdown("## 4. Ejemplo guiado: dos operadores")
st.markdown(
    """
    <div class="example-box">
        <b>Situación:</b> llega un cliente cada <b>10 minutos</b>. Cada operador tarda en promedio <b>15 minutos</b> por atención,
        pero existen <b>2 operadores</b> trabajando en paralelo. ¿La capacidad conjunta es suficiente y cuánto espera el cliente?
    </div>
    """,
    unsafe_allow_html=True,
)

r_e = calcular_mms(10.0, 15.0, 2)
paso1, paso2, paso3 = st.tabs(["1 · Convertir", "2 · Resultados", "3 · Interpretar"])
with paso1:
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("λ", f"{r_e['lambda']:.1f} clientes/h")
    p2.metric("μ por servidor", f"{r_e['mu']:.1f} clientes/h")
    p3.metric("Servidores", "2")
    p4.metric("Capacidad conjunta", f"{2*r_e['mu']:.1f} clientes/h")
    st.success("La demanda es 6 clientes/h y la capacidad conjunta es 8 clientes/h: el sistema es estable.")
with paso2:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Utilización", f"{r_e['rho']*100:.1f}%")
    m2.metric("Prob. de esperar", f"{r_e['P_espera']*100:.1f}%")
    m3.metric("Clientes en cola", f"{r_e['Lq']:.2f}")
    m4.metric("Espera Wq", f"{r_e['Wq']*60:.1f} min")
    m5.metric("Tiempo total W", f"{r_e['W']*60:.1f} min")
with paso3:
    st.markdown(
        f"""
        <div class="success-box">
            <b>Lectura operativa:</b> cada servidor trabaja, en promedio, al <b>{r_e['rho']*100:.1f}%</b> de utilización.
            Aun con capacidad suficiente, aproximadamente <b>{r_e['P_espera']*100:.1f}%</b> de los clientes encuentra todos los servidores ocupados
            al llegar y debe esperar. El tiempo promedio en cola es de <b>{r_e['Wq']*60:.1f} minutos</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("## 5. Laboratorio interactivo: cambia la dotación")
st.markdown("Modifica los tres datos y observa cómo la misma demanda responde cuando cambia la cantidad de servidores.")

l1, l2, l3 = st.columns(3)
with l1:
    t_llegada = st.slider("Llega 1 cliente cada... (min)", 1.0, 30.0, 10.0, 0.5)
with l2:
    t_atencion = st.slider("Cada atención tarda... (min)", 1.0, 30.0, 15.0, 0.5)
with l3:
    servidores = st.slider("Número de servidores", 1, 10, 2, 1)

r_lab = calcular_mms(t_llegada, t_atencion, servidores)
render_sistema_mms(r_lab, "Tu escenario interactivo")

if not r_lab["estable"]:
    st.markdown(
        f"""
        <div class="critical-box">
            <b>⚠️ Capacidad insuficiente.</b> Llegan aproximadamente <b>{r_lab['lambda']:.1f} clientes/h</b>, mientras la capacidad conjunta
            es de <b>{servidores*r_lab['mu']:.1f} clientes/h</b>. Con esta dotación la cola no tiene equilibrio de largo plazo.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric("Utilización", f"{r_lab['rho']*100:.1f}%")
    q2.metric("Prob. de esperar", f"{r_lab['P_espera']*100:.1f}%")
    q3.metric("Cola promedio", f"{r_lab['Lq']:.2f}")
    q4.metric("Espera Wq", f"{r_lab['Wq']*60:.1f} min")
    q5.metric("Tiempo total", f"{r_lab['W']*60:.1f} min")

    if t_llegada < t_atencion:
        st.info("Cada servidor individual atiende más lento que el ritmo de llegada, pero la capacidad conjunta puede compensarlo. Observa ρ y Wq para evaluar el sistema completo.")

st.plotly_chart(grafico_operadores(t_llegada, t_atencion, max_s=10, actual=servidores), use_container_width=True)
st.caption("El gráfico muestra el efecto marginal de agregar servidores. Después de cierto punto, cada servidor adicional genera una reducción cada vez menor de la espera.")

# EDU_INTERPRETATION_MMS
st.markdown(to_markdown(interpret_mms(r_lab, servidores)))

# EDU_MARGINAL_MMS_04
st.markdown(marginal_mms_markdown(t_llegada, t_atencion, servidores))

st.markdown("## 6. Reto de destreza: encuentra la dotación")
st.markdown(
    """
    <div class="skill-box">
        <b>Reto:</b> llega un cliente cada <b>5 minutos</b> y cada atención tarda <b>12 minutos</b>.
        Ajusta la cantidad de servidores hasta lograr una espera promedio de <b>5 minutos o menos</b>.
        No se valida memoria: se valida que puedas dimensionar la capacidad observando el comportamiento del sistema.
    </div>
    """,
    unsafe_allow_html=True,
)

reto_s = st.slider("Servidores para el reto", 1, 8, 3, 1, key="reto_mms")
r_reto = calcular_mms(5.0, 12.0, reto_s)
if not r_reto["estable"]:
    st.error("La capacidad aún es insuficiente. Aumenta la cantidad de servidores.")
else:
    rr1, rr2, rr3 = st.columns(3)
    rr1.metric("Utilización", f"{r_reto['rho']*100:.1f}%")
    rr2.metric("Prob. de esperar", f"{r_reto['P_espera']*100:.1f}%")
    rr3.metric("Espera Wq", f"{r_reto['Wq']*60:.2f} min")
    if r_reto["Wq"] * 60 <= 5:
        st.success("✅ Reto logrado. Encontraste una dotación que cumple la meta de servicio. Ahora prueba si puedes reducir un servidor sin perder el objetivo.")
    else:
        st.warning("La configuración es estable, pero aún no cumple la meta de 5 minutos. Evalúa un servidor adicional.")

st.markdown("## 7. Qué debes llevarte de este módulo")
st.markdown(
    """
    - En M/M/s, la capacidad relevante es la suma de los **s servidores**.
    - Un sistema puede ser estable y aun tener una probabilidad alta de espera.
    - Agregar servidores reduce la congestión, pero el beneficio marginal no es infinito.
    - **ρ**, **P(espera)** y **Wq** deben interpretarse juntos para tomar decisiones de capacidad.
    - La destreza se demuestra dimensionando escenarios y justificando la decisión, no respondiendo preguntas de memoria.
    """
)

st.info("Siguiente paso recomendado: estudiar sistemas con capacidad finita para comprender qué ocurre cuando el sistema puede llenarse y comenzar a rechazar clientes.")
