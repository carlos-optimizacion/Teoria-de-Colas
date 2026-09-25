import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from queue_core import economic_cost, mms_from_minutes

st.set_page_config(page_title="22 - Análisis Económico | Colas", page_icon="💰", layout="wide")

st.markdown("""
<style>
.stApp{background:#F7F9FC}.block-container{padding-top:1.1rem;max-width:1450px}
.hero{background:linear-gradient(135deg,#12324D,#1F5A86 60%,#2D7BA8);color:white;border-radius:24px;padding:28px 32px;box-shadow:0 14px 30px rgba(23,50,77,.15)}
.hero h1{margin:0;font-size:2.1rem}.hero p{margin:.6rem 0 0;opacity:.94;max-width:1000px}
.callout{background:#EEF6FB;border:1px solid #CFE0EC;border-left:6px solid #1F5A86;border-radius:14px;padding:15px 18px;margin:.5rem 0 1rem}
.ok{background:#EAF7EF;border:1px solid #C8E4D1;border-left:6px solid #15803D;border-radius:14px;padding:15px 18px;margin:.5rem 0 1rem}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E7EE;padding:13px 15px;border-radius:14px}
</style>
""",unsafe_allow_html=True)

st.markdown("""
<div class="hero"><div style="font-size:.76rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;opacity:.82">Economía de operaciones · Servicio vs costo</div>
<h1>22. ¿Cuánto cuesta reducir la espera?</h1>
<p>Evalúa el equilibrio entre agregar operadores y reducir el tiempo que los clientes permanecen esperando. El objetivo es comprender el costo total del sistema, no minimizar una métrica aislada.</p></div>
""",unsafe_allow_html=True)

st.markdown("## 1. Datos del proceso")
c1,c2,c3=st.columns(3)
with c1:
    t_llegada=st.number_input("Llega 1 cliente cada... (min)",min_value=.1,value=4.0,step=.5)
with c2:
    t_atencion=st.number_input("Atención promedio (min)",min_value=.1,value=6.0,step=.5)
with c3:
    max_s=st.number_input("Evaluar hasta... operadores",min_value=1,value=10,step=1)

st.markdown("## 2. Costos y meta de servicio")
e1,e2,e3=st.columns(3)
with e1:
    costo_operador=st.number_input("Costo de un operador (S//h)",min_value=0.0,value=20.0,step=1.0)
with e2:
    costo_espera=st.number_input("Costo estimado de 1 cliente-hora de espera (S/)",min_value=0.0,value=12.0,step=1.0,help="Representa el impacto económico asignado al tiempo de clientes esperando: pérdida de productividad, abandono, penalidades o valor del tiempo.")
with e3:
    meta_wq=st.number_input("Meta máxima de espera (min)",min_value=0.1,value=5.0,step=.5)

filas=[]
for s in range(1,int(max_s)+1):
    r=mms_from_minutes(t_llegada,t_atencion,s)
    if not r["estable"]:
        filas.append({"Operadores":s,"Estado":"Inestable","Utilización %":r["rho"]*100,"Espera (min)":None,"Costo personal":s*costo_operador,"Costo espera":None,"Costo total":None,"Cumple meta":"No"})
        continue
    c=economic_cost(r,s,costo_operador,costo_espera)
    filas.append({"Operadores":s,"Estado":"Estable","Utilización %":r["rho"]*100,"Espera (min)":r["Wq"]*60,"Costo personal":c["personal"],"Costo espera":c["espera"],"Costo total":c["total"],"Cumple meta":"Sí" if r["Wq"]*60<=meta_wq else "No"})

df=pd.DataFrame(filas)
estables=df[df["Estado"]=="Estable"].copy()

st.markdown("## 3. Lee el costo total")
fig=go.Figure()
fig.add_trace(go.Bar(x=estables["Operadores"],y=estables["Costo personal"],name="Capacidad / personal"))
fig.add_trace(go.Bar(x=estables["Operadores"],y=estables["Costo espera"],name="Espera de clientes"))
fig.update_layout(title="Composición del costo por cantidad de operadores",xaxis_title="Operadores",yaxis_title="Costo estimado por hora (S/)",barmode="stack",template="plotly_white",height=430)
st.plotly_chart(fig,use_container_width=True)
st.caption("Agregar operadores eleva el costo de capacidad, pero puede reducir con fuerza el costo asociado a la espera. El punto conveniente depende de los costos que definas.")

st.markdown("## 4. Decisión con restricción de servicio")
cumple=estables[estables["Cumple meta"]=="Sí"]
if cumple.empty:
    st.warning("Ninguna alternativa evaluada cumple la meta de espera. Amplía el rango de operadores o mejora el tiempo de atención.")
else:
    recomendado=cumple.sort_values("Costo total").iloc[0]
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Operadores sugeridos",int(recomendado["Operadores"]))
    m2.metric("Espera",f"{recomendado['Espera (min)']:.1f} min")
    m3.metric("Utilización",f"{recomendado['Utilización %']:.1f}%")
    m4.metric("Costo total",f"S/ {recomendado['Costo total']:.2f}/h")
    st.markdown(f'<div class="ok"><b>Criterio usado:</b> entre las alternativas que cumplen una espera ≤ {meta_wq:.1f} min, se selecciona la de menor costo total estimado por hora. Con tus supuestos, corresponde a <b>{int(recomendado["Operadores"])} operadores</b>.</div>',unsafe_allow_html=True)

with st.expander("Ver tabla económica completa"):
    st.dataframe(df.style.format({"Utilización %":"{:.1f}","Espera (min)":"{:.1f}","Costo personal":"S/ {:.2f}","Costo espera":"S/ {:.2f}","Costo total":"S/ {:.2f}"},na_rep="—"),use_container_width=True)

st.markdown('<div class="callout"><b>Importante:</b> el costo de espera no es una tarifa contable automática. Es un parámetro de decisión que debe estimarse con información real del proceso: valor del tiempo, abandono, penalidades, pérdida de ventas o impacto de servicio. La herramienta muestra cómo cambia la decisión cuando ese costo cambia.</div>',unsafe_allow_html=True)
