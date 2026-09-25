import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from interpretation_core import interpret_mmsk, to_markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="06 - M/M/s/K | Laboratorio", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.stApp { background:#F7F9FC; }
.block-container { padding-top:1.1rem; padding-bottom:2.6rem; max-width:1450px; }
.hero { background:linear-gradient(135deg,#12324D 0%,#1F5A86 58%,#2D7BA8 100%); border-radius:24px; padding:30px 34px; color:white; box-shadow:0 16px 34px rgba(23,50,77,.16); margin-bottom:1rem; }
.hero h1 { margin:0; font-size:2.15rem; } .hero p { margin:.7rem 0 0; opacity:.94; max-width:1050px; }
.eyebrow { font-size:.76rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; opacity:.82; }
.card { background:white; border:1px solid #E3E9F0; border-radius:16px; padding:18px 20px; box-shadow:0 5px 16px rgba(31,78,120,.05); min-height:128px; }
.card h4 { margin:0 0 .45rem; color:#17324D; } .card p { margin:0; color:#5A6675; }
.example { background:#fff; border:1px solid #DDE5EC; border-left:6px solid #1F5A86; border-radius:16px; padding:18px 20px; margin:.5rem 0 1rem; }
.warn { background:#FFF7E6; border:1px solid #F0D9AB; border-left:6px solid #D97706; border-radius:14px; padding:16px 18px; margin:.45rem 0 1rem; color:#75440A; }
.skill { background:linear-gradient(135deg,#F0F6FB 0%,#FFFFFF 100%); border:1px solid #CDDFEC; border-radius:18px; padding:20px 22px; margin:.5rem 0 1rem; }
div[data-testid="stMetric"] { background:#fff; border:1px solid #E1E7EE; padding:14px 16px; border-radius:14px; box-shadow:0 4px 12px rgba(31,78,120,.04); }
#MainMenu { visibility:hidden; } footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


def calcular_mmsk(t_llegada, t_atencion, s, K):
    lam = 60.0 / t_llegada
    mu = 60.0 / t_atencion
    s, K = int(s), int(K)
    if K < s:
        raise ValueError("K debe ser mayor o igual al número de servidores.")

    pesos = [1.0]
    for n in range(1, K + 1):
        salida = min(n, s) * mu
        pesos.append(pesos[-1] * lam / salida)
    total = sum(pesos)
    p = [x / total for x in pesos]
    p_bloqueo = p[-1]
    lam_eff = lam * (1 - p_bloqueo)
    L = sum(n * p[n] for n in range(K + 1))
    ocupados = lam_eff / mu
    Lq = max(0.0, L - ocupados)
    W = L / lam_eff if lam_eff > 0 else float("inf")
    Wq = Lq / lam_eff if lam_eff > 0 else float("inf")
    util = ocupados / s
    p_espera = sum(p[s:K]) if K > s else 0.0
    return {"lambda":lam,"mu":mu,"s":s,"K":K,"P":p,"P_bloqueo":p_bloqueo,"lambda_eff":lam_eff,"L":L,"Lq":Lq,"W":W,"Wq":Wq,"rho":util,"P_espera":p_espera}


def render_diagrama(r, titulo):
    s, K = r["s"], r["K"]
    espera_max = max(0, K - s)
    ocup_visual = min(5, max(1, int(math.ceil(r["Lq"])))) if espera_max > 0 else 0
    puestos = min(5, espera_max)
    cola = ""
    for i in range(puestos):
        x = 325 + i*42
        fill = "#527A9E" if i < ocup_visual else "#DDE6EE"
        cola += f'<circle cx="{x}" cy="150" r="10" fill="{fill}"/><rect x="{x-11}" y="163" width="22" height="26" rx="6" fill="{fill}"/>'
    servidores = ""
    vis = min(4, s)
    for i in range(vis):
        y = 118 + i*45
        servidores += f'<rect x="690" y="{y}" width="175" height="36" rx="11" fill="#EAF7EF" stroke="#B7DDC5"/><text x="778" y="{y+23}" text-anchor="middle" font-size="13" font-weight="700" fill="#14532D">Servidor {i+1}</text>'
    extra_s = "" if s <= 4 else f"+ {s-4} servidores"
    extra_k = "" if espera_max <= 5 else f"+ {espera_max-5} lugares de espera"
    html = f"""
    <html><body style="margin:0;background:#F7F9FC;font-family:Arial,sans-serif;">
    <div style="background:#fff;border:1px solid #E1E8EF;border-radius:22px;padding:10px;">
    <svg viewBox="0 0 1180 365" width="100%">
      <defs><marker id="aK" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#7B8EA3"/></marker></defs>
      <rect x="8" y="8" width="1164" height="349" rx="22" fill="#F3F8FC"/>
      <text x="40" y="48" font-size="24" font-weight="700" fill="#17324D">{titulo}</text>
      <text x="40" y="73" font-size="14" fill="#667085">Capacidad total K = servicio + espera. Cuando el sistema llega a K, la siguiente llegada es bloqueada.</text>
      <rect x="35" y="105" width="205" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/>
      <rect x="280" y="105" width="295" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/>
      <rect x="635" y="95" width="275" height="175" rx="18" fill="#fff" stroke="#DCE6EF"/>
      <rect x="955" y="105" width="190" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/>
      <line x1="240" y1="182" x2="275" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#aK)"/>
      <line x1="575" y1="182" x2="630" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#aK)"/>
      <line x1="910" y1="182" x2="950" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#aK)"/>
      <text x="137" y="155" text-anchor="middle" font-size="24">👥</text><text x="137" y="212" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Llegadas</text><text x="137" y="235" text-anchor="middle" font-size="12.5" fill="#667085">λ = {r['lambda']:.2f}/h</text>
      {cola}
      <text x="427" y="218" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Espera limitada</text>
      <text x="427" y="239" text-anchor="middle" font-size="12.5" fill="#667085">máx. {espera_max} esperando · {extra_k}</text>
      {servidores}
      <text x="775" y="286" text-anchor="middle" font-size="13" font-weight="700" fill="#17324D">{s} servidor(es) · {extra_s}</text>
      <circle cx="1050" cy="155" r="28" fill="#FDECEC" stroke="#F2C7C7"/><text x="1050" y="163" text-anchor="middle" font-size="24">↪</text>
      <text x="1050" y="212" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Salida / bloqueo</text>
      <text x="1050" y="235" text-anchor="middle" font-size="12.5" fill="#667085">P(bloqueo) = {r['P_bloqueo']*100:.1f}%</text>
      <rect x="40" y="300" width="1095" height="40" rx="18" fill="#EAF1F7"/>
      <text x="590" y="325" text-anchor="middle" font-size="14" font-weight="700" fill="#1F4E78">Utilización: {r['rho']*100:.1f}% · Cola media: {r['Lq']:.2f} · Espera: {r['Wq']*60:.1f} min · Clientes aceptados: {r['lambda_eff']:.2f}/h</text>
    </svg></div></body></html>
    """
    components.html(html, height=410, scrolling=False)


def grafico_capacidad(t_llegada, t_atencion, s, k_min, k_max):
    filas=[]
    for K in range(k_min, k_max+1):
        r=calcular_mmsk(t_llegada,t_atencion,s,K)
        filas.append({"K":K,"Bloqueo":r["P_bloqueo"]*100,"Wq":r["Wq"]*60})
    df=pd.DataFrame(filas)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df["K"],y=df["Bloqueo"],mode="lines+markers",name="Clientes bloqueados (%)",line=dict(width=4),hovertemplate="K=%{x}<br>Bloqueo=%{y:.1f}%<extra></extra>"))
    fig.update_layout(title="Cómo cambia el rechazo cuando aumenta la capacidad total",xaxis_title="Capacidad total K",yaxis_title="Probabilidad de bloqueo (%)",template="plotly_white",height=420,margin=dict(l=30,r=20,t=70,b=40))
    fig.update_xaxes(dtick=1)
    return fig


st.markdown("""
<div class="hero"><div class="eyebrow">Modo Aprendizaje · Capacidad finita</div><h1>06. Modelo M/M/s/K</h1>
<p>Aprende qué ocurre cuando un sistema tiene varios servidores, pero solo admite un número máximo de clientes. Aquí aparece una nueva decisión: equilibrar espera y rechazo.</p></div>
""", unsafe_allow_html=True)

st.markdown("## 1. ¿Qué aprenderás?")
a,b,c,d=st.columns(4)
with a: st.markdown('<div class="card"><h4>🏠 Capacidad</h4><p>Distinguir servidores, lugares de espera y capacidad total K.</p></div>',unsafe_allow_html=True)
with b: st.markdown('<div class="card"><h4>🚫 Bloqueo</h4><p>Entender por qué un cliente puede no ingresar cuando el sistema está lleno.</p></div>',unsafe_allow_html=True)
with c: st.markdown('<div class="card"><h4>🧪 Experimentar</h4><p>Cambiar K y observar rechazo, espera y clientes aceptados.</p></div>',unsafe_allow_html=True)
with d: st.markdown('<div class="card"><h4>💡 Decidir</h4><p>Reconocer el compromiso entre capacidad física y nivel de servicio.</p></div>',unsafe_allow_html=True)

st.markdown("## 2. Visualiza el límite físico")
r0=calcular_mmsk(12,10,2,5)
render_diagrama(r0,"Ejemplo visual · dos servidores y capacidad total K = 5")
st.markdown("En este ejemplo pueden existir como máximo **5 clientes dentro del sistema**: hasta 2 en servicio y hasta 3 esperando. Si llega un sexto cliente cuando los cinco lugares están ocupados, no ingresa.")

st.markdown("## 3. La idea clave")
st.markdown('<div class="warn"><b>K no es la longitud de la cola.</b> K es la capacidad total: clientes siendo atendidos + clientes esperando. Por eso siempre debe cumplirse K ≥ s.</div>',unsafe_allow_html=True)
with st.expander("Ver formulación probabilística",expanded=False):
    st.markdown("El modelo se resuelve como una cadena nacimiento–muerte finita. Para cada estado n, la tasa de salida es min(n,s)·μ. La probabilidad de bloqueo es la probabilidad del estado lleno: **P(K)**.")
    st.latex(r"\lambda_{ef}=\lambda(1-P_K)")
    st.latex(r"W=\frac{L}{\lambda_{ef}}\qquad ;\qquad W_q=\frac{L_q}{\lambda_{ef}}")

st.markdown("## 4. Ejemplo guiado")
st.markdown('<div class="example"><b>Situación:</b> llega un cliente cada 12 min, cada atención dura 10 min, hay 2 servidores y solo caben 5 clientes en total.</div>',unsafe_allow_html=True)
e1,e2,e3,e4,e5=st.columns(5)
e1.metric("Utilización",f"{r0['rho']*100:.1f}%")
e2.metric("Bloqueo",f"{r0['P_bloqueo']*100:.1f}%")
e3.metric("Aceptados",f"{r0['lambda_eff']:.2f}/h")
e4.metric("Cola media",f"{r0['Lq']:.2f}")
e5.metric("Espera",f"{r0['Wq']*60:.1f} min")
st.info("En sistemas finitos, incluso una demanda intensa no produce una cola infinita: el precio de la capacidad limitada es el bloqueo de llegadas.")

st.markdown("## 5. Laboratorio interactivo")
x1,x2,x3,x4=st.columns(4)
with x1: tl=st.slider("Llega 1 cliente cada... (min)",1.0,30.0,12.0,.5)
with x2: ta=st.slider("Atención promedio (min)",1.0,30.0,10.0,.5)
with x3: s=st.slider("Servidores",1,8,2)
with x4: K=st.slider("Capacidad total K",s,max(s,20),max(s,5))
r=calcular_mmsk(tl,ta,s,K)
render_diagrama(r,"Tu escenario interactivo")
m1,m2,m3,m4,m5=st.columns(5)
m1.metric("Utilización",f"{r['rho']*100:.1f}%")
m2.metric("Bloqueo",f"{r['P_bloqueo']*100:.1f}%")
m3.metric("Prob. de esperar",f"{r['P_espera']*100:.1f}%")
m4.metric("Wq",f"{r['Wq']*60:.1f} min")
m5.metric("Aceptados",f"{r['lambda_eff']:.2f}/h")
st.plotly_chart(grafico_capacidad(tl,ta,s,s,min(20,max(s+6,K+3))),use_container_width=True)
st.caption("Aumentar K suele reducir el rechazo, pero permite que más clientes permanezcan esperando. El mejor tamaño depende del nivel de servicio y del costo de perder clientes.")

# EDU_INTERPRETATION_MMSK
r_interpretacion = dict(r)
r_interpretacion.setdefault("lambda_efectiva", r.get("lambda_eff", r.get("lambda", 0.0)))
st.markdown(to_markdown(interpret_mmsk(r_interpretacion)))

st.markdown("## 6. Reto de destreza")
st.markdown('<div class="skill"><b>Reto:</b> con llegadas cada 6 min, atención de 8 min y 2 servidores, ajusta K hasta conseguir una probabilidad de bloqueo menor o igual al 5 %.</div>',unsafe_allow_html=True)
k_reto=st.slider("Capacidad K para el reto",2,15,5,key="reto_mmsk")
rr=calcular_mmsk(6,8,2,k_reto)
r1,r2,r3=st.columns(3)
r1.metric("K",k_reto); r2.metric("Bloqueo",f"{rr['P_bloqueo']*100:.2f}%"); r3.metric("Wq",f"{rr['Wq']*60:.1f} min")
if rr["P_bloqueo"]<=.05: st.success("✅ Reto logrado. La capacidad seleccionada mantiene el bloqueo en 5 % o menos.")
else: st.warning("Aún se rechaza más del 5 % de las llegadas. Incrementa K y observa el cambio.")

st.markdown("## 7. Qué debes llevarte")
st.markdown("- **K** limita el número total de clientes dentro del sistema.\n- Cuando el sistema está lleno aparece **bloqueo**.\n- La tasa efectiva de llegada es menor que λ cuando se pierden clientes.\n- Más capacidad reduce rechazo, pero puede aumentar la cantidad de clientes esperando.\n- La decisión correcta equilibra espacio, espera y clientes perdidos.")
st.info("Siguiente paso: analiza el caso particular con un solo servidor y una cola de espera limitada.")
