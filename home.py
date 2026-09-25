import streamlit as st

st.set_page_config(page_title="Teoría de Colas | Decision Lab", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp{background:#F6F8FB}.block-container{padding-top:1.3rem;padding-bottom:2rem;max-width:1450px}
.hero{background:linear-gradient(135deg,#163A5F 0%,#1F4E78 58%,#2D6A9F 100%);border-radius:22px;padding:30px 34px;color:white;box-shadow:0 12px 30px rgba(23,50,77,.16);margin-bottom:1.1rem}
.hero h1{margin:0;font-size:2.3rem;line-height:1.12}.hero p{margin:.65rem 0 0;font-size:1.02rem;opacity:.93;max-width:980px}
.eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;opacity:.80}
.mode-card{background:#fff;border:1px solid #E5EAF0;border-radius:18px;padding:22px 24px;min-height:310px;box-shadow:0 6px 18px rgba(31,78,120,.06)}
.mode-card h3{margin-top:0;color:#17324D}.mode-card p{color:#5A6675}.pill{display:inline-block;background:#EAF1F7;color:#1F4E78;border-radius:999px;padding:5px 10px;font-size:.78rem;font-weight:700;margin-bottom:8px}
.flow{background:#fff;border:1px solid #E6EBF1;border-radius:16px;padding:16px 18px;text-align:center;min-height:105px}.flow strong{color:#1F4E78}.small-note{color:#6B7280;font-size:.88rem}
#MainMenu{visibility:hidden}footer{visibility:hidden}
</style>
""",unsafe_allow_html=True)

st.markdown("""
<div class="hero"><div class="eyebrow">Investigación de Operaciones · Ingeniería Industrial</div>
<h1>Teoría de Colas | Decision Lab</h1>
<p>Plataforma para aprender visualmente, validar supuestos, experimentar con escenarios y convertir datos de espera en decisiones de capacidad, servicio y costo.</p></div>
""",unsafe_allow_html=True)

st.markdown("### Elige cómo quieres trabajar")
c1,c2,c3=st.columns(3,gap="large")

with c1:
    st.markdown("""
    <div class="mode-card"><span class="pill">MODO APRENDIZAJE</span><h3>Comprender haciendo</h3>
    <p>Ruta progresiva para entender cada modelo antes de aplicarlo.</p><b>Incluye</b><ul>
    <li>Diagramas visuales del sistema</li><li>Explicaciones intuitivas</li><li>Ejemplos paso a paso</li><li>Laboratorios con parámetros modificables</li><li>Retos de destreza sin preguntas memorísticas</li>
    </ul></div>
    """,unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="mode-card"><span class="pill">LABORATORIO APLICADO</span><h3>Probar decisiones operativas</h3>
    <p>Ruta 18–24 para trabajar casos, capacidad, economía y diagnóstico de supuestos.</p><b>Permite</b><ul>
    <li>Resolver casos de hospital, banca y producción</li><li>Construir escenarios M/M/1 y M/M/s</li><li>Analizar capacidad finita y bloqueo</li><li>Comparar alternativas y costos</li><li>Revisar datos antes de elegir el modelo</li>
    </ul></div>
    """,unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="mode-card"><span class="pill">MODO ANALISTA</span><h3>Dimensionar un sistema real</h3>
    <p>Ruta End-to-End para transformar datos de campo en una recomendación ejecutiva.</p><b>Responde</b><ul>
    <li>¿La dotación actual soporta la demanda?</li><li>¿Cuánto espera el cliente?</li><li>¿Cuántos operadores necesito?</li><li>¿Cuál es el costo-beneficio?</li><li>¿Qué escenario debería documentarse?</li>
    </ul></div>
    """,unsafe_allow_html=True)

st.markdown("### Flujo de la plataforma")
f1,f2,f3,f4,f5=st.columns(5)
with f1: st.markdown('<div class="flow"><strong>1. Comprende</strong><br><span class="small-note">Conoce el modelo</span></div>',unsafe_allow_html=True)
with f2: st.markdown('<div class="flow"><strong>2. Valida</strong><br><span class="small-note">Revisa supuestos</span></div>',unsafe_allow_html=True)
with f3: st.markdown('<div class="flow"><strong>3. Experimenta</strong><br><span class="small-note">Modifica parámetros</span></div>',unsafe_allow_html=True)
with f4: st.markdown('<div class="flow"><strong>4. Compara</strong><br><span class="small-note">Servicio y costo</span></div>',unsafe_allow_html=True)
with f5: st.markdown('<div class="flow"><strong>5. Decide</strong><br><span class="small-note">Sustenta la recomendación</span></div>',unsafe_allow_html=True)

st.info("Para aprender desde cero inicia en **01. Fundamentos**. Para trabajar aplicaciones usa **18–23**. Antes de aplicar un modelo a datos reales revisa **24. Validador de Supuestos** y luego continúa con **25. Análisis End-to-End**.")
st.markdown("---")
st.caption("Mag. Carlos Alberto Nieto Astahuamán · Aplicación educativa desarrollada con fines académicos. Los resultados dependen de los supuestos del modelo y deben contrastarse con el comportamiento real del proceso.")
