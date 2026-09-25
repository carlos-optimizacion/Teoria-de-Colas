import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from queue_core import mms_from_minutes, mmsk_from_minutes

st.set_page_config(page_title="21 - Comparador de Escenarios", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
.stApp{background:#F7F9FC}.block-container{padding-top:1.1rem;max-width:1450px}
.hero{background:linear-gradient(135deg,#12324D,#1F5A86 60%,#2D7BA8);color:white;border-radius:24px;padding:28px 32px;box-shadow:0 14px 30px rgba(23,50,77,.15)}
.hero h1{margin:0;font-size:2.1rem}.hero p{margin:.6rem 0 0;opacity:.94;max-width:1000px}
.panel{background:#fff;border:1px solid #E3E9F0;border-radius:18px;padding:18px 20px;box-shadow:0 5px 16px rgba(31,78,120,.05)}
.ok{background:#EAF7EF;border:1px solid #C8E4D1;border-left:6px solid #15803D;border-radius:14px;padding:14px 17px;margin:.5rem 0}
.warn{background:#FFF7E6;border:1px solid #F0D9AB;border-left:6px solid #D97706;border-radius:14px;padding:14px 17px;margin:.5rem 0}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E7EE;padding:13px 15px;border-radius:14px}
</style>
""",unsafe_allow_html=True)


def captura_escenario(prefijo, titulo, defaults):
    st.markdown(f"### {titulo}")
    t_llegada=st.number_input("Llegada: 1 cliente cada... (min)",min_value=.1,value=defaults[0],step=.5,key=f"tl_{prefijo}")
    t_atencion=st.number_input("Atención promedio (min)",min_value=.1,value=defaults[1],step=.5,key=f"ta_{prefijo}")
    s=st.number_input("Servidores",min_value=1,value=defaults[2],step=1,key=f"s_{prefijo}")
    finita=st.toggle("Capacidad total limitada",value=False,key=f"fin_{prefijo}")
    k=None
    if finita:
        k=st.number_input("Capacidad total K",min_value=int(s),value=max(int(s)+3,5),step=1,key=f"k_{prefijo}")
        r=mmsk_from_minutes(t_llegada,t_atencion,int(s),int(k))
    else:
        r=mms_from_minutes(t_llegada,t_atencion,int(s))
    return {"titulo":titulo,"t_llegada":t_llegada,"t_atencion":t_atencion,"s":int(s),"finita":finita,"K":k,"r":r}


st.markdown("""
<div class="hero"><div style="font-size:.76rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;opacity:.82">Comparación aplicada · Decidir con criterios</div>
<h1>21. Compara dos escenarios operativos</h1>
<p>No compares fórmulas: compara decisiones. Define una situación actual y una alternativa, fija una meta de servicio y observa qué configuración cumple mejor el objetivo.</p></div>
""",unsafe_allow_html=True)

st.markdown("## 1. Configura los dos escenarios")
a,b=st.columns(2,gap="large")
with a:
    esc_a=captura_escenario("a","Escenario A · actual",(4.0,6.0,2))
with b:
    esc_b=captura_escenario("b","Escenario B · alternativa",(4.0,6.0,3))

st.markdown("## 2. Define qué significa buen servicio")
c1,c2=st.columns(2)
with c1:
    meta_wq=st.slider("Espera promedio máxima (min)",1.0,30.0,5.0,.5)
with c2:
    meta_bloqueo=st.slider("Bloqueo máximo si hay capacidad finita (%)",0.0,20.0,5.0,.5)

filas=[]
for e in [esc_a,esc_b]:
    r=e["r"]
    wq=r["Wq"]*60 if r["estable"] and math.isfinite(r["Wq"]) else None
    bloqueo=r["P_bloqueo"]*100
    cumple=(r["estable"] and wq is not None and wq<=meta_wq and bloqueo<=meta_bloqueo)
    filas.append({
        "Escenario":e["titulo"],"Servidores":e["s"],"Capacidad":"∞" if not e["finita"] else int(e["K"]),
        "Utilización %":r["rho"]*100,"Prob. espera %":r["P_espera"]*100,"Espera (min)":wq,
        "Bloqueo %":bloqueo,"Cumple meta":"Sí" if cumple else "No"
    })
df=pd.DataFrame(filas)

st.markdown("## 3. Resultado comparativo")
st.dataframe(df.style.format({"Utilización %":"{:.1f}","Prob. espera %":"{:.1f}","Espera (min)":"{:.1f}","Bloqueo %":"{:.1f}"}),use_container_width=True)

fig=go.Figure()
fig.add_trace(go.Bar(x=df["Escenario"],y=df["Espera (min)"],name="Espera promedio"))
fig.add_hline(y=meta_wq,line_dash="dash",annotation_text="Meta de espera")
fig.update_layout(title="La comparación principal: tiempo de espera",yaxis_title="Minutos",template="plotly_white",height=410,showlegend=False)
st.plotly_chart(fig,use_container_width=True)

st.markdown("## 4. Interpreta la decisión")
for _,row in df.iterrows():
    if row["Cumple meta"]=="Sí":
        st.markdown(f'<div class="ok"><b>{row["Escenario"]}</b> cumple las metas: espera {row["Espera (min)"]:.1f} min y bloqueo {row["Bloqueo %"]:.1f}%.</div>',unsafe_allow_html=True)
    else:
        espera_txt="inestable" if pd.isna(row["Espera (min)"]) else f'{row["Espera (min)"]:.1f} min'
        st.markdown(f'<div class="warn"><b>{row["Escenario"]}</b> no cumple al menos un criterio. Espera: {espera_txt}; bloqueo: {row["Bloqueo %"]:.1f}%.</div>',unsafe_allow_html=True)

cumplen=df[df["Cumple meta"]=="Sí"]
if len(cumplen)==2:
    menor_dot=cumplen.sort_values(["Servidores","Espera (min)"]).iloc[0]
    st.info(f"Ambos escenarios cumplen. Si el criterio adicional es usar menor dotación, {menor_dot['Escenario']} requiere {int(menor_dot['Servidores'])} servidor(es). La decisión económica se puede revisar en el módulo 22.")
elif len(cumplen)==1:
    st.success(f"Solo {cumplen.iloc[0]['Escenario']} cumple simultáneamente las metas definidas.")
else:
    st.warning("Ninguno cumple las metas. Ajusta servidores, velocidad de atención o capacidad y vuelve a comparar.")

st.caption("Los modelos con capacidad infinita requieren ρ < 1. Los modelos con capacidad finita siempre tienen un número finito de estados, pero pueden presentar bloqueo elevado.")
