import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from queue_core import mms_from_minutes

st.set_page_config(page_title="19 - Escenarios M/M/s | Laboratorio", page_icon="🧪", layout="wide")

st.markdown("""
<style>
.stApp{background:#F7F9FC}.block-container{padding-top:1.1rem;max-width:1450px}
.hero{background:linear-gradient(135deg,#12324D,#1F5A86 60%,#2D7BA8);color:white;border-radius:24px;padding:28px 32px;box-shadow:0 14px 30px rgba(23,50,77,.15)}
.hero h1{margin:0;font-size:2.1rem}.hero p{margin:.6rem 0 0;opacity:.94;max-width:1000px}
.card{background:#fff;border:1px solid #E3E9F0;border-radius:16px;padding:18px 20px;box-shadow:0 5px 16px rgba(31,78,120,.05)}
.callout{background:#EEF6FB;border:1px solid #CFE0EC;border-left:6px solid #1F5A86;border-radius:14px;padding:15px 18px;margin:.5rem 0 1rem}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E7EE;padding:13px 15px;border-radius:14px}
</style>
""", unsafe_allow_html=True)


def render_queue(servers, result):
    srv = "".join([f"<div class='srv'>👤<br>Servidor {i+1}</div>" for i in range(servers)])
    estado = "Estable" if result["estable"] else "Inestable"
    color = "#15803D" if result["estable"] else "#B42318"
    cola = f"Lq = {result['Lq']:.2f}" if result["estable"] else "cola creciente"
    html=f"""
    <html><head><style>
    body{{margin:0;font-family:Arial,sans-serif;background:#F7F9FC}}
    .wrap{{background:white;border:1px solid #E2E8F0;border-radius:18px;padding:18px}}
    .row{{display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap}}
    .box,.srv{{padding:14px 16px;border-radius:14px;text-align:center;font-weight:700;color:#17324D;min-width:115px}}
    .box{{background:#F0F5FA;border:1px solid #CEDBE8}}.srv{{background:#EAF7EF;border:1px solid #C8E4D1;min-width:92px}}
    .servers{{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}}.arrow{{font-size:24px;color:#7B8EA3}}
    .status{{margin-top:14px;text-align:center;font-weight:700;color:{color}}}
    </style></head><body><div class='wrap'><div class='row'>
    <div class='box'>👥 Llegadas<br><small>λ={result['lambda']:.1f}/h</small></div><div class='arrow'>→</div>
    <div class='box'>🧍🧍 Cola<br><small>{cola}</small></div><div class='arrow'>→</div><div class='servers'>{srv}</div><div class='arrow'>→</div><div class='box'>✅ Salida</div>
    </div><div class='status'>{estado} · utilización {result['rho']*100:.1f}%</div></div></body></html>"""
    components.html(html, height=190, scrolling=False)


st.markdown("""
<div class="hero"><div style="font-size:.76rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;opacity:.82">Laboratorio aplicado · Capacidad infinita</div>
<h1>19. Construye un escenario M/M/1 o M/M/s</h1>
<p>Trabaja con datos que se observan en campo: cada cuánto llega un cliente, cuánto tarda la atención y cuántos servidores operan. La aplicación calcula las tasas y traduce el resultado a experiencia de servicio.</p></div>
""", unsafe_allow_html=True)

st.markdown("## 1. Define la operación")
c1,c2,c3=st.columns(3)
with c1:
    t_llegada=st.slider("Llega 1 cliente cada... (min)",1.0,30.0,6.0,.5)
with c2:
    t_atencion=st.slider("Cada atención tarda... (min)",1.0,30.0,4.0,.5)
with c3:
    servidores=st.slider("Servidores",1,10,1)

r=mms_from_minutes(t_llegada,t_atencion,servidores)
render_queue(servidores,r)

st.markdown("## 2. Lee el sistema")
if not r["estable"]:
    st.error("La capacidad agregada no alcanza para absorber la demanda. En un modelo de capacidad infinita la cola tenderá a crecer sin límite.")
else:
    m1,m2,m3,m4,m5=st.columns(5)
    m1.metric("Utilización",f"{r['rho']*100:.1f}%")
    m2.metric("Prob. de esperar",f"{r['P_espera']*100:.1f}%")
    m3.metric("Clientes en cola",f"{r['Lq']:.2f}")
    m4.metric("Espera Wq",f"{r['Wq']*60:.1f} min")
    m5.metric("Tiempo total W",f"{r['W']*60:.1f} min")
    st.markdown(f'<div class="callout"><b>Interpretación:</b> con {servidores} servidor(es), el cliente espera en promedio <b>{r["Wq"]*60:.1f} minutos</b> antes de iniciar su atención. La probabilidad de encontrar todos los servidores ocupados es aproximadamente <b>{r["P_espera"]*100:.1f}%</b>.</div>',unsafe_allow_html=True)

st.markdown("## 3. ¿Qué cambia si modificas la dotación?")
filas=[]
for s in range(1,11):
    rr=mms_from_minutes(t_llegada,t_atencion,s)
    filas.append({"Servidores":s,"Utilización %":rr["rho"]*100,"Espera (min)":rr["Wq"]*60 if rr["estable"] else None,"Prob. espera %":rr["P_espera"]*100 if rr["estable"] else 100,"Estado":"Estable" if rr["estable"] else "Inestable"})
df=pd.DataFrame(filas)
fig=go.Figure()
fig.add_trace(go.Scatter(x=df["Servidores"],y=df["Espera (min)"],mode="lines+markers",name="Espera promedio"))
fig.update_layout(title="Tiempo de espera según número de servidores",xaxis_title="Servidores",yaxis_title="Espera promedio (min)",template="plotly_white",height=420)
st.plotly_chart(fig,use_container_width=True)

with st.expander("Ver tabla de escenarios"):
    st.dataframe(df.style.format({"Utilización %":"{:.1f}","Espera (min)":"{:.1f}","Prob. espera %":"{:.1f}"}),use_container_width=True)

st.markdown("## 4. Reto de destreza")
meta=st.slider("Meta máxima de espera (min)",1.0,20.0,5.0,.5)
candidatos=df[(df["Estado"]=="Estable") & (df["Espera (min)"]<=meta)]
if candidatos.empty:
    st.warning("Ninguna dotación entre 1 y 10 servidores cumple la meta. Revisa la velocidad de atención o amplía el rango de capacidad.")
else:
    minimo=int(candidatos.iloc[0]["Servidores"])
    st.success(f"Para este escenario, la menor dotación que cumple una espera promedio ≤ {meta:.1f} min es {minimo} servidor(es). Cambia los datos y comprueba cómo cambia la decisión.")

st.info("Este laboratorio utiliza M/M/1 cuando hay un servidor y M/M/s cuando hay varios. Ambos suponen una sola cola, capacidad de espera no limitada y servidores equivalentes.")
