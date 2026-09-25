import math

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="24 - Validador de Supuestos", page_icon="🔎", layout="wide")

st.markdown(
    """
    <style>
    .stApp{background:#F7F9FC}.block-container{padding-top:1.1rem;max-width:1450px}
    .hero{background:linear-gradient(135deg,#12324D,#1F5A86 60%,#2D7BA8);color:white;border-radius:24px;padding:28px 32px;box-shadow:0 14px 30px rgba(23,50,77,.15)}
    .hero h1{margin:0;font-size:2.1rem}.hero p{margin:.6rem 0 0;opacity:.94;max-width:1100px}
    .ok{background:#EAF7EF;border:1px solid #C8E4D1;border-left:6px solid #15803D;border-radius:14px;padding:15px 18px;margin:.5rem 0 1rem}
    .warn{background:#FFF7E6;border:1px solid #F0D9AB;border-left:6px solid #D97706;border-radius:14px;padding:15px 18px;margin:.5rem 0 1rem}
    .info{background:#EEF6FB;border:1px solid #CFE0EC;border-left:6px solid #1F5A86;border-radius:14px;padding:15px 18px;margin:.5rem 0 1rem}
    div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E7EE;padding:13px 15px;border-radius:14px}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div style="font-size:.76rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;opacity:.82">Calidad del modelo · Datos reales</div>
      <h1>24. ¿Mis datos son compatibles con los supuestos?</h1>
      <p>Explora tiempos entre llegadas y tiempos de servicio antes de elegir M/M/1 o M/M/s. Este módulo realiza un diagnóstico descriptivo preliminar; no sustituye una prueba estadística formal ni una validación del proceso.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## 1. Carga tus observaciones")
st.write(
    "Sube un CSV donde cada fila represente una observación. Idealmente incluye una columna de **tiempo entre llegadas (min)** y otra de **tiempo de servicio (min)**."
)

with st.expander("Ver ejemplo de estructura"):
    st.code(
        "interarribo_min,servicio_min\n4.2,6.1\n3.7,5.8\n5.1,7.0\n4.5,6.4",
        language="text",
    )

archivo = st.file_uploader("Archivo CSV", type=["csv"])

if archivo is None:
    st.info("Carga un archivo para iniciar el diagnóstico. Si todavía no tienes datos, usa los módulos teóricos solo como escenarios exploratorios y documenta explícitamente los supuestos.")
    st.stop()

try:
    df = pd.read_csv(archivo)
except Exception as exc:
    st.error(f"No se pudo leer el archivo: {exc}")
    st.stop()

if df.empty:
    st.error("El archivo no contiene observaciones.")
    st.stop()

columnas_numericas = df.select_dtypes(include="number").columns.tolist()
if not columnas_numericas:
    st.error("No se encontraron columnas numéricas en el archivo.")
    st.stop()

st.markdown("## 2. Selecciona las variables")
c1, c2 = st.columns(2)
with c1:
    col_llegada = st.selectbox("Tiempo entre llegadas (min)", columnas_numericas, index=0)
with c2:
    opciones_servicio = [c for c in columnas_numericas if c != col_llegada] or columnas_numericas
    col_servicio = st.selectbox("Tiempo de servicio (min)", opciones_servicio, index=0)


def limpiar_serie(serie):
    s = pd.to_numeric(serie, errors="coerce").dropna()
    return s[s > 0]


def resumen(serie):
    n = len(serie)
    media = float(serie.mean()) if n else float("nan")
    std = float(serie.std(ddof=1)) if n > 1 else float("nan")
    cv = std / media if n > 1 and media > 0 else float("nan")
    ac1 = float(serie.autocorr(lag=1)) if n > 2 else float("nan")
    return {"n": n, "media": media, "std": std, "cv": cv, "ac1": ac1}


def lectura_cv(cv):
    if not math.isfinite(cv):
        return "Muestra insuficiente"
    if 0.8 <= cv <= 1.2:
        return "CV cercano a 1"
    if cv < 0.8:
        return "Variabilidad menor que exponencial"
    return "Variabilidad mayor que exponencial"


def lectura_dependencia(ac1):
    if not math.isfinite(ac1):
        return "Muestra insuficiente"
    if abs(ac1) <= 0.2:
        return "Dependencia lineal baja en lag 1"
    return "Posible dependencia temporal"


llegadas = limpiar_serie(df[col_llegada])
servicios = limpiar_serie(df[col_servicio])
r_llegadas = resumen(llegadas)
r_servicios = resumen(servicios)

if r_llegadas["n"] < 20 or r_servicios["n"] < 20:
    st.warning("La muestra es pequeña para evaluar el patrón con confianza. El diagnóstico se mostrará, pero conviene recolectar más observaciones antes de sustentar el modelo.")

st.markdown("## 3. Diagnóstico descriptivo")
left, right = st.columns(2)

with left:
    st.markdown("### Llegadas")
    a1, a2, a3 = st.columns(3)
    a1.metric("Observaciones", r_llegadas["n"])
    a2.metric("Media", f"{r_llegadas['media']:.2f} min" if math.isfinite(r_llegadas["media"]) else "—")
    a3.metric("CV", f"{r_llegadas['cv']:.2f}" if math.isfinite(r_llegadas["cv"]) else "—")
    st.caption(f"{lectura_cv(r_llegadas['cv'])}. {lectura_dependencia(r_llegadas['ac1'])}.")

with right:
    st.markdown("### Servicio")
    b1, b2, b3 = st.columns(3)
    b1.metric("Observaciones", r_servicios["n"])
    b2.metric("Media", f"{r_servicios['media']:.2f} min" if math.isfinite(r_servicios["media"]) else "—")
    b3.metric("CV", f"{r_servicios['cv']:.2f}" if math.isfinite(r_servicios["cv"]) else "—")
    st.caption(f"{lectura_cv(r_servicios['cv'])}. {lectura_dependencia(r_servicios['ac1'])}.")

st.markdown("## 4. Visualiza la variabilidad")
g1, g2 = st.columns(2)
with g1:
    fig_l = px.histogram(llegadas.to_frame(name="Interarribo"), x="Interarribo", nbins=25, title="Distribución observada de tiempos entre llegadas")
    fig_l.update_layout(template="plotly_white", xaxis_title="Minutos", yaxis_title="Frecuencia")
    st.plotly_chart(fig_l, use_container_width=True)
with g2:
    fig_s = px.histogram(servicios.to_frame(name="Servicio"), x="Servicio", nbins=25, title="Distribución observada de tiempos de servicio")
    fig_s.update_layout(template="plotly_white", xaxis_title="Minutos", yaxis_title="Frecuencia")
    st.plotly_chart(fig_s, use_container_width=True)

st.markdown("## 5. Compatibilidad preliminar del modelo")
llegada_cv_ok = math.isfinite(r_llegadas["cv"]) and 0.8 <= r_llegadas["cv"] <= 1.2
servicio_cv_ok = math.isfinite(r_servicios["cv"]) and 0.8 <= r_servicios["cv"] <= 1.2
llegada_dep_ok = math.isfinite(r_llegadas["ac1"]) and abs(r_llegadas["ac1"]) <= 0.2
servicio_dep_ok = math.isfinite(r_servicios["ac1"]) and abs(r_servicios["ac1"]) <= 0.2

if llegada_cv_ok and servicio_cv_ok and llegada_dep_ok and servicio_dep_ok:
    st.markdown(
        '<div class="ok"><b>Resultado preliminar:</b> los CV son cercanos a 1 y la autocorrelación lag-1 es baja. Esto es compatible, de forma descriptiva, con usar M/M/1 o M/M/s como primera aproximación. No constituye una demostración formal de exponencialidad o proceso Poisson.</div>',
        unsafe_allow_html=True,
    )
elif llegada_cv_ok and llegada_dep_ok and not servicio_cv_ok:
    st.markdown(
        '<div class="warn"><b>Servicio no claramente exponencial:</b> las llegadas son razonablemente compatibles con el supuesto M, pero la variabilidad del servicio se aparta de CV≈1. Con un servidor, M/G/1 puede ser una alternativa más apropiada; con varios servidores conviene evaluar simulación o un modelo más general.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="warn"><b>Revisar antes de usar M/M/s:</b> la variabilidad o la dependencia temporal observada no respalda claramente los supuestos simples. Conviene segmentar por franja horaria, revisar estabilidad del proceso y considerar simulación de eventos discretos.</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="info"><b>Importante:</b> CV≈1 es solo una señal descriptiva. Una validación académica más fuerte puede incorporar pruebas de ajuste, gráficos Q-Q, análisis por intervalos, estacionariedad y revisión del mecanismo generador de llegadas.</div>',
    unsafe_allow_html=True,
)

st.markdown("## 6. Datos depurados para continuar")
resumen_df = pd.DataFrame(
    [
        {
            "Variable": "Interarribos",
            "n": r_llegadas["n"],
            "Media (min)": r_llegadas["media"],
            "Desv. estándar": r_llegadas["std"],
            "CV": r_llegadas["cv"],
            "Autocorr. lag 1": r_llegadas["ac1"],
        },
        {
            "Variable": "Servicio",
            "n": r_servicios["n"],
            "Media (min)": r_servicios["media"],
            "Desv. estándar": r_servicios["std"],
            "CV": r_servicios["cv"],
            "Autocorr. lag 1": r_servicios["ac1"],
        },
    ]
)
st.dataframe(resumen_df.style.format({"Media (min)": "{:.3f}", "Desv. estándar": "{:.3f}", "CV": "{:.3f}", "Autocorr. lag 1": "{:.3f}"}, na_rep="—"), use_container_width=True, hide_index=True)
st.download_button("Descargar resumen diagnóstico (CSV)", data=resumen_df.to_csv(index=False).encode("utf-8"), file_name="diagnostico_supuestos_colas.csv", mime="text/csv")
