import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from queue_core import mmsk_from_minutes

st.set_page_config(page_title="20 - Capacidad Finita | Laboratorio", page_icon="🚦", layout="wide")

st.markdown("""
<style>
.stApp{background:#F7F9FC}.block-container{padding-top:1.1rem;max-width:1450px}
.hero{background:linear-gradient(135deg,#12324D,#1F5A86 60%,#2D7BA8);color:white;border-radius:24px;padding:28px 32px;box-shadow:0 14px 30px rgba(23,50,77,.15)}
.hero h1{margin:0;font-size:2.1rem}.hero p{margin:.6rem 0 0;opacity:.94;max-width:1000px}
.callout{background:#EEF6FB;border:1px solid #CFE0EC;border-left:6px solid #1F5A86;border-radius:14px;padding:15px 18px;margin:.5rem 0 1rem}
.warn{background:#FFF7E6;border:1px solid #F0D9AB;border-left:6px solid #D97706;border-radius:14px;padding:15px 18px;margin:.5rem 0 1rem}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E7EE;padding:13px 15px;border-radius:14px}
</style>
""", unsafe_allow_html=True)


def render_capacidad(s,k,r):
    srv="".join([f"<div class='srv'>👤<br>S{i+1}</div>" for i in range(s)])
    espera=max(0,k-s)
    html=f"""
    <html><head><style>
    body{{margin:0;font-family:Arial,sans-serif;background:#F7F9FC}}
    .wrap{{background:white;border:1px solid #E2E8F0;border-radius:18px;padding:18px}}
    .row{{display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap}}
    .box,.srv{{padding:14px 16px;border-radius:14px;text-align:center;font-weight:700;color:#17324D;min-width:115px}}
    .box{{background:#F0F5FA;border:1px solid #CEDBE8}}.cap{{background:#FFF7E6;border:1px solid #F0D9AB}}
    .srv{{background:#EAF7EF;border:1px solid #C8E4D1;min-width:78px}}.servers{{display:flex;gap:7px;flex-wrap:wrap;justify-content:center}}
    .arrow{{font-size:24px;color:#7B8EA3}}.lost{{color:#B42318;font-weight:700;text-align:center;margin-top:12px}}
    </style></head><body><div class='wrap'><div class='row'>
    <div class='box'>👥 Llegadas<br><small>{r['lambda']:.1f}/h</small></div><div class='arrow'>→</div>
    <div class='box cap'>Capacidad total K={k}<br><small>{s} en servicio + hasta {espera} esperando</small></div><div class='arrow'>→</div>
    <div class='servers'>{srv}</div><div class='arrow'>→</div><div class='box'>✅ Atendidos</div>
    </div><div class='lost'>Si el sistema llega a K, el siguiente cliente se bloquea · P(bloqueo)={r['P_bloqueo']*100:.1f}%</div></div></body></html>"""
    components.html(html,height=205,scrolling=False)


st.markdown("""
<div class="hero"><div style="font-size:.76rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;opacity:.82">Laboratorio aplicado · Capacidad finita</div>
<h1>20. ¿Qué pasa cuando el sistema se llena?</h1>
<p>Analiza sistemas donde existe un máximo físico o comercial de clientes dentro del proceso. Cuando se alcanza K, nuevas llegadas no pueden ingresar y aparece el bloqueo.</p></div>
""",unsafe_allow_html=True)

st.markdown("## 1. Define el sistema")
c1,c2,c3,c4=st.columns(4)
with c1:
    t_llegada=st.slider("Llega 1 cliente cada... (min)",1.0,30.0,5.0,.5)
with c2:
    t_atencion=st.slider("Cada atención tarda... (min)",1.0,30.0,6.0,.5)
with c3:
    s=st.slider("Servidores",1,8,2)
with c4:
    k=st.slider("Capacidad total K",s,max(s+1,20),max(s+3,5))

r=mmsk_from_minutes(t_llegada,t_atencion,s,k)
render_capacidad(s,k,r)

st.markdown("## 2. Indicadores que importan")
m1,m2,m3,m4,m5=st.columns(5)
m1.metric("Utilización efectiva",f"{r['rho']*100:.1f}%")
m2.metric("Bloqueo",f"{r['P_bloqueo']*100:.1f}%")
m3.metric("Llegadas admitidas",f"{r['lambda_efectiva']:.2f}/h")
m4.metric("Espera Wq",f"{r['Wq']*60:.1f} min")
m5.metric("Cola promedio",f"{r['Lq']:.2f}")

st.markdown(f'<div class="callout"><b>Interpretación:</b> de cada 100 llegadas, aproximadamente <b>{r["P_bloqueo"]*100:.1f}</b> encontrarían el sistema lleno. Quienes sí ingresan esperan en promedio <b>{r["Wq"]*60:.1f} minutos</b> antes de ser atendidos.</div>',unsafe_allow_html=True)

st.markdown("## 3. ¿Dónde pasa el tiempo el sistema?")
df_estados=pd.DataFrame({"Clientes en el sistema":list(range(k+1)),"Probabilidad":r["probs"]})
fig=go.Figure(go.Bar(x=df_estados["Clientes en el sistema"],y=df_estados["Probabilidad"]*100))
fig.update_layout(title="Probabilidad de encontrar n clientes en el sistema",xaxis_title="Clientes dentro del sistema",yaxis_title="Probabilidad (%)",template="plotly_white",height=400)
st.plotly_chart(fig,use_container_width=True)
st.caption("La última barra corresponde al estado lleno K; esa probabilidad es también la probabilidad de bloqueo por PASTA.")

st.markdown("## 4. Explora el efecto de ampliar la capacidad")
filas=[]
for kk in range(s,max(s+1,20)+1):
    rr=mmsk_from_minutes(t_llegada,t_atencion,s,kk)
    filas.append({"K":kk,"Bloqueo %":rr["P_bloqueo"]*100,"Espera admitidos (min)":rr["Wq"]*60,"Clientes admitidos/h":rr["lambda_efectiva"]})
df=pd.DataFrame(filas)
fig2=go.Figure()
fig2.add_trace(go.Scatter(x=df["K"],y=df["Bloqueo %"],mode="lines+markers",name="Bloqueo %"))
fig2.update_layout(title="Cómo cambia el bloqueo al ampliar la capacidad",xaxis_title="Capacidad total K",yaxis_title="Probabilidad de bloqueo (%)",template="plotly_white",height=410)
st.plotly_chart(fig2,use_container_width=True)

meta=st.slider("Reto: bloqueo máximo aceptable (%)",0.5,20.0,5.0,.5)
cumple=df[df["Bloqueo %"]<=meta]
if cumple.empty:
    st.warning("Con la dotación actual, ninguna capacidad evaluada cumple la meta. Puede ser necesario aumentar servidores o acelerar la atención.")
else:
    kmin=int(cumple.iloc[0]["K"])
    st.success(f"La menor capacidad total dentro del rango evaluado que cumple un bloqueo ≤ {meta:.1f}% es K={kmin}.")

st.markdown('<div class="warn"><b>Nota de notación:</b> en los módulos previos puede aparecer c para representar capacidad. En este laboratorio usamos <b>K</b> como capacidad total del sistema porque evita confundirla con el número de servidores.</div>',unsafe_allow_html=True)
