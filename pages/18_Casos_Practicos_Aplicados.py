import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from interpretation_core import marginal_mms_markdown
from interpretation_core import interpret_dd1, interpret_mms, to_markdown
import streamlit.components.v1 as components

from queue_core import dd1_sequence, mms_from_minutes

st.set_page_config(page_title="18 - Casos Aplicados | Laboratorio", page_icon="🧩", layout="wide")

st.markdown("""
<style>
.stApp { background:#F7F9FC; }
.block-container { padding-top:1.1rem; max-width:1450px; }
.hero { background:linear-gradient(135deg,#12324D,#1F5A86 60%,#2D7BA8); color:white; border-radius:24px; padding:28px 32px; box-shadow:0 14px 30px rgba(23,50,77,.15); }
.hero h1 { margin:0; font-size:2.1rem; }
.hero p { margin:.6rem 0 0; opacity:.94; max-width:1000px; }
.card { background:white; border:1px solid #E3E9F0; border-radius:16px; padding:18px 20px; box-shadow:0 5px 16px rgba(31,78,120,.05); }
.case { background:#FFFFFF; border:1px solid #DDE5EC; border-left:6px solid #1F5A86; border-radius:16px; padding:18px 20px; margin:.6rem 0 1rem; }
.warn { background:#FFF7E6; border:1px solid #F0D9AB; border-left:6px solid #D97706; border-radius:14px; padding:15px 18px; }
.ok { background:#EAF7EF; border:1px solid #C8E4D1; border-left:6px solid #15803D; border-radius:14px; padding:15px 18px; }
div[data-testid="stMetric"] { background:#fff; border:1px solid #E1E7EE; padding:13px 15px; border-radius:14px; }
</style>
""", unsafe_allow_html=True)


def render_flujo(servidores=1, titulo="Sistema de atención"):
    operadores = "".join([f"<div class='srv'>Operador {i+1}</div>" for i in range(servidores)])
    html = f"""
    <html><head><style>
    body{{margin:0;font-family:Arial,sans-serif;background:#F7F9FC}}
    .wrap{{background:white;border:1px solid #E2E8F0;border-radius:18px;padding:18px 20px}}
    .title{{font-weight:700;color:#17324D;margin-bottom:14px;font-size:18px}}
    .flow{{display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap}}
    .box,.srv{{border-radius:14px;padding:14px 18px;text-align:center;font-weight:700;color:#17324D;min-width:120px}}
    .box{{background:#F0F5FA;border:1px solid #CEDBE8}}
    .srv{{background:#EAF7EF;border:1px solid #C8E4D1;min-width:100px}}
    .servers{{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}}
    .arrow{{font-size:24px;color:#7B8EA3;font-weight:800}}
    </style></head><body><div class='wrap'><div class='title'>{titulo}</div><div class='flow'>
    <div class='box'>👥 Llegadas</div><div class='arrow'>→</div><div class='box'>🧍🧍 Cola</div><div class='arrow'>→</div>
    <div class='servers'>{operadores}</div><div class='arrow'>→</div><div class='box'>✅ Salida</div>
    </div></div></body></html>
    """
    components.html(html, height=165, scrolling=False)


st.markdown("""
<div class="hero">
<div style="font-size:.76rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;opacity:.82">Aplicación · Aprender resolviendo</div>
<h1>18. Casos prácticos aplicados</h1>
<p>Selecciona un contexto, modifica sus condiciones y observa cómo cambia la espera. El objetivo es elegir el modelo correcto y traducir sus resultados a una decisión operativa.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## 1. Elige un caso")
caso = st.selectbox("Caso de estudio", ["🏥 Emergencias hospitalarias", "🏦 Ventanillas bancarias", "🏭 Estación automatizada D/D/1"])

if caso == "🏥 Emergencias hospitalarias":
    st.markdown('<div class="case"><b>Situación:</b> pacientes llegan de manera aleatoria a una zona de atención con varios médicos equivalentes. El modelo base es <b>M/M/s</b>.</div>', unsafe_allow_html=True)
    render_flujo(3, "Hospital · una cola y médicos en paralelo")
    c1, c2, c3 = st.columns(3)
    with c1:
        t_llegada = st.slider("Llega 1 paciente cada... (min)", 2.0, 30.0, 10.0, 0.5)
    with c2:
        t_atencion = st.slider("Cada médico tarda... (min)", 5.0, 40.0, 20.0, 0.5)
    with c3:
        s = st.slider("Médicos disponibles", 1, 8, 3)

    r = mms_from_minutes(t_llegada, t_atencion, s)
    if not r["estable"]:
        st.markdown('<div class="warn"><b>⚠️ Capacidad insuficiente:</b> con esta dotación la demanda iguala o supera la capacidad agregada.</div>', unsafe_allow_html=True)
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Utilización", f"{r['rho']*100:.1f}%")
        m2.metric("Prob. de esperar", f"{r['P_espera']*100:.1f}%")
        m3.metric("Espera promedio", f"{r['Wq']*60:.1f} min")
        m4.metric("Pacientes en cola", f"{r['Lq']:.2f}")
        st.markdown(f'<div class="ok"><b>Lectura operativa:</b> con {s} médicos, un paciente espera en promedio <b>{r["Wq"]*60:.1f} min</b>. Prueba aumentar o reducir médicos y observa el costo de operar con mayor o menor capacidad.</div>', unsafe_allow_html=True)

elif caso == "🏦 Ventanillas bancarias":
    st.markdown('<div class="case"><b>Situación:</b> clientes llegan a una sola fila y son derivados a varias ventanillas. El modelo base es <b>M/M/s</b>.</div>', unsafe_allow_html=True)
    render_flujo(2, "Banco · una cola y varias ventanillas")
    c1, c2, c3 = st.columns(3)
    with c1:
        t_llegada = st.slider("Llega 1 cliente cada... (min)", 1.0, 15.0, 3.0, 0.25)
    with c2:
        t_atencion = st.slider("Cada atención tarda... (min)", 1.0, 15.0, 5.0, 0.25)
    with c3:
        s = st.slider("Ventanillas abiertas", 1, 8, 2)

    r = mms_from_minutes(t_llegada, t_atencion, s)
    if not r["estable"]:
        st.error("La configuración es inestable: la capacidad agregada no absorbe el ritmo de llegada.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Utilización", f"{r['rho']*100:.1f}%")
        m2.metric("Prob. de esperar", f"{r['P_espera']*100:.1f}%")
        m3.metric("Espera Wq", f"{r['Wq']*60:.1f} min")
        m4.metric("Tiempo total W", f"{r['W']*60:.1f} min")
        st.info("Reto: encuentra la menor cantidad de ventanillas que mantenga la espera por debajo de 5 minutos.")

else:
    st.markdown('<div class="case"><b>Situación:</b> las piezas llegan y se procesan a intervalos constantes. Aquí la variabilidad desaparece y usamos <b>D/D/1</b>.</div>', unsafe_allow_html=True)
    render_flujo(1, "Producción automatizada · flujo determinista")
    c1, c2 = st.columns(2)
    with c1:
        T = st.slider("Intervalo entre piezas T (min)", 1.0, 10.0, 4.0, 0.25)
    with c2:
        S = st.slider("Tiempo de proceso S (min)", 1.0, 10.0, 3.0, 0.25)

    filas = dd1_sequence(T, S, 12)
    df = pd.DataFrame(filas)
    rho = S / T
    m1, m2, m3 = st.columns(3)
    m1.metric("Utilización", f"{rho*100:.1f}%")
    m2.metric("Espera cliente 12", f"{df.iloc[-1]['Espera (min)']:.1f} min")
    m3.metric("Máx. espera observada", f"{df['Espera (min)'].max():.1f} min")

    fig = go.Figure(go.Scatter(x=df["Cliente"], y=df["Espera (min)"], mode="lines+markers"))
    fig.update_layout(title="Evolución de la espera cliente a cliente", xaxis_title="Cliente", yaxis_title="Espera (min)", template="plotly_white", height=380)
    st.plotly_chart(fig, use_container_width=True)
    if S <= T:
        st.success("Como el proceso termina antes o justo cuando llega la siguiente pieza, la espera no se acumula en este esquema sincronizado.")
    else:
        st.warning("El tiempo de proceso supera el intervalo entre llegadas: la espera se acumula cliente a cliente.")

# EDU_INTERPRETATION_CASES
if caso in {"🏥 Emergencias hospitalarias", "🏦 Ventanillas bancarias"}:
    st.markdown(
        to_markdown(
            interpret_mms(r, s),
            title=f"🧠 Interpretación del caso: {caso}",
        )
    )
else:
    st.markdown(
        to_markdown(
            interpret_dd1(
                T,
                S,
                float(df["Espera (min)"].mean()),
                float(df.iloc[-1]["Espera (min)"]),
            ),
            title="🧠 Interpretación del caso de producción",
        )
    )

# EDU_MARGINAL_MMS_18
if caso in {"🏥 Emergencias hospitalarias", "🏦 Ventanillas bancarias"}:
    st.markdown(marginal_mms_markdown(t_llegada, t_atencion, s, title="🔬 ¿Qué pasa con un recurso menos o uno más?"))

st.markdown("## 2. Qué debe demostrar el estudiante")
st.markdown("""
- Identificar qué característica del proceso determina el modelo.
- Explicar qué provoca la espera o el bloqueo.
- Modificar una decisión operativa —servidores, capacidad o velocidad— y justificar el efecto observado.
- Traducir los indicadores a una conclusión comprensible para operaciones.
""")

st.info("Siguiente paso: usa los módulos 19 y 20 para construir escenarios propios y el módulo 21 para compararlos.")
