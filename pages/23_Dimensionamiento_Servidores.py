import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from queue_core import mms_from_minutes

st.set_page_config(page_title="23 - Dimensionamiento de Servidores", page_icon="👥", layout="wide")

st.markdown("""
<style>
.stApp{background:#F7F9FC}.block-container{padding-top:1.1rem;max-width:1450px}
.hero{background:linear-gradient(135deg,#12324D,#1F5A86 60%,#2D7BA8);color:white;border-radius:24px;padding:28px 32px;box-shadow:0 14px 30px rgba(23,50,77,.15)}
.hero h1{margin:0;font-size:2.1rem}.hero p{margin:.6rem 0 0;opacity:.94;max-width:1000px}
.ok{background:#EAF7EF;border:1px solid #C8E4D1;border-left:6px solid #15803D;border-radius:14px;padding:15px 18px;margin:.5rem 0 1rem}
.warn{background:#FFF7E6;border:1px solid #F0D9AB;border-left:6px solid #D97706;border-radius:14px;padding:15px 18px;margin:.5rem 0 1rem}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E7EE;padding:13px 15px;border-radius:14px}
</style>
""",unsafe_allow_html=True)

st.markdown("""
<div class="hero"><div style="font-size:.76rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;opacity:.82">Capacidad operativa · Nivel de servicio</div>
<h1>23. ¿Cuántos servidores necesito?</h1>
<p>Parte de la dotación actual, define hasta cuántos servidores quieres evaluar y establece una meta de espera. La herramienta muestra el efecto marginal de agregar capacidad.</p></div>
""",unsafe_allow_html=True)

st.markdown("## 1. Datos reales de la operación")
c1,c2,c3,c4=st.columns(4)
with c1:
    t_llegada=st.number_input("Llega 1 cliente cada... (min)",min_value=.1,value=4.0,step=.5)
with c2:
    t_atencion=st.number_input("Atención promedio (min)",min_value=.1,value=6.0,step=.5)
with c3:
    actual=st.number_input("Servidores actuales",min_value=1,value=2,step=1)
with c4:
    max_s=st.number_input("Evaluar hasta... servidores",min_value=int(actual),value=max(int(actual)+5,8),step=1)

meta=st.slider("Meta máxima de espera promedio (min)",1.0,30.0,5.0,.5)

filas=[]
for s in range(1,int(max_s)+1):
    r=mms_from_minutes(t_llegada,t_atencion,s)
    filas.append({
        "Servidores":s,
        "Estado":"Estable" if r["estable"] else "Inestable",
        "Utilización %":r["rho"]*100,
        "Prob. espera %":r["P_espera"]*100 if r["estable"] else 100,
        "Espera (min)":r["Wq"]*60 if r["estable"] else None,
        "Cola promedio":r["Lq"] if r["estable"] else None,
    })
df=pd.DataFrame(filas)

st.markdown("## 2. Situación actual")
r_actual=mms_from_minutes(t_llegada,t_atencion,int(actual))
if not r_actual["estable"]:
    st.markdown('<div class="warn"><b>⚠️ Dotación actual insuficiente:</b> la capacidad agregada no absorbe la demanda promedio. Antes de discutir nivel de servicio, se requiere aumentar capacidad o reducir el tiempo de atención.</div>',unsafe_allow_html=True)
else:
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Utilización",f"{r_actual['rho']*100:.1f}%")
    m2.metric("Prob. de esperar",f"{r_actual['P_espera']*100:.1f}%")
    m3.metric("Espera actual",f"{r_actual['Wq']*60:.1f} min")
    m4.metric("Cola promedio",f"{r_actual['Lq']:.2f}")

st.markdown("## 3. Curva de servicio")
fig=go.Figure()
fig.add_trace(go.Scatter(x=df["Servidores"],y=df["Espera (min)"],mode="lines+markers",name="Espera promedio"))
fig.add_hline(y=meta,line_dash="dash",annotation_text="Meta")
fig.add_vline(x=int(actual),line_dash="dot",annotation_text="Dotación actual")
fig.update_layout(title="Tiempo de espera según cantidad de servidores",xaxis_title="Servidores",yaxis_title="Espera promedio (min)",template="plotly_white",height=430)
st.plotly_chart(fig,use_container_width=True)
st.caption("La curva permite ver cuándo agregar un servidor produce una mejora relevante y cuándo los beneficios adicionales empiezan a ser pequeños.")

st.markdown("## 4. Dotación mínima para la meta")
candidatos=df[(df["Estado"]=="Estable") & (df["Espera (min)"]<=meta)]
if candidatos.empty:
    st.warning("No se alcanza la meta dentro del rango evaluado. Amplía el máximo de servidores o analiza mejoras en el tiempo de atención.")
else:
    recomendado=int(candidatos.iloc[0]["Servidores"])
    rr=mms_from_minutes(t_llegada,t_atencion,recomendado)
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Dotación mínima",recomendado,delta=f"{recomendado-int(actual):+d} vs actual")
    m2.metric("Espera resultante",f"{rr['Wq']*60:.1f} min")
    m3.metric("Utilización",f"{rr['rho']*100:.1f}%")
    m4.metric("Prob. de esperar",f"{rr['P_espera']*100:.1f}%")
    st.markdown(f'<div class="ok"><b>Lectura operativa:</b> para una meta de espera ≤ {meta:.1f} min, la menor dotación que la cumple es <b>{recomendado} servidores</b>. El módulo 22 permite añadir el criterio económico antes de tomar una decisión final.</div>',unsafe_allow_html=True)

with st.expander("Ver todos los escenarios"):
    st.dataframe(df.style.format({"Utilización %":"{:.1f}","Prob. espera %":"{:.1f}","Espera (min)":"{:.1f}","Cola promedio":"{:.2f}"},na_rep="—"),use_container_width=True)

st.info("Este módulo utiliza M/M/s: llegadas Poisson, tiempos de servicio exponenciales, una sola cola y servidores equivalentes. Para una decisión integral con costos y reporte ejecutivo, continúa al Modo Analista End-to-End.")
