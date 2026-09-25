import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from interpretation_core import interpret_mmsk, to_markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="08 - M/M/1/c | Laboratorio", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.stApp{background:#F7F9FC}.block-container{padding-top:1.1rem;padding-bottom:2.6rem;max-width:1450px}
.hero{background:linear-gradient(135deg,#12324D 0%,#1F5A86 58%,#2D7BA8 100%);border-radius:24px;padding:30px 34px;color:white;box-shadow:0 16px 34px rgba(23,50,77,.16);margin-bottom:1rem}
.hero h1{margin:0;font-size:2.15rem}.hero p{margin:.7rem 0 0;opacity:.94;max-width:1050px}.eyebrow{font-size:.76rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;opacity:.82}
.card{background:white;border:1px solid #E3E9F0;border-radius:16px;padding:18px 20px;box-shadow:0 5px 16px rgba(31,78,120,.05);min-height:128px}.card h4{margin:0 0 .45rem;color:#17324D}.card p{margin:0;color:#5A6675}
.example{background:#fff;border:1px solid #DDE5EC;border-left:6px solid #1F5A86;border-radius:16px;padding:18px 20px;margin:.5rem 0 1rem}.warn{background:#FFF7E6;border:1px solid #F0D9AB;border-left:6px solid #D97706;border-radius:14px;padding:16px 18px;margin:.45rem 0 1rem;color:#75440A}.skill{background:linear-gradient(135deg,#F0F6FB 0%,#FFFFFF 100%);border:1px solid #CDDFEC;border-radius:18px;padding:20px 22px;margin:.5rem 0 1rem}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E7EE;padding:14px 16px;border-radius:14px;box-shadow:0 4px 12px rgba(31,78,120,.04)}#MainMenu{visibility:hidden}footer{visibility:hidden}
</style>
""",unsafe_allow_html=True)


def calcular_mm1c(t_llegada,t_atencion,c):
    lam=60.0/t_llegada
    mu=60.0/t_atencion
    c=int(c)
    K=c+1
    rho=lam/mu
    if abs(rho-1.0)<1e-12:
        probs=[1/(K+1)]*(K+1)
    else:
        p0=(1-rho)/(1-rho**(K+1))
        probs=[p0*(rho**n) for n in range(K+1)]
    p_block=probs[-1]
    lam_eff=lam*(1-p_block)
    L=sum(n*probs[n] for n in range(K+1))
    ocupado=lam_eff/mu
    Lq=max(0.0,L-ocupado)
    W=L/lam_eff if lam_eff>0 else float('inf')
    Wq=Lq/lam_eff if lam_eff>0 else float('inf')
    p_wait=sum(probs[1:K])
    return {"lambda":lam,"mu":mu,"rho_nominal":rho,"c":c,"K":K,"P":probs,"P_bloqueo":p_block,"lambda_eff":lam_eff,"L":L,"Lq":Lq,"W":W,"Wq":Wq,"ocupacion":ocupado,"P_espera":p_wait}


def render_diagrama(r,titulo):
    c=r['c']
    slots=min(6,c)
    personas=min(slots,max(0,int(math.ceil(r['Lq']))))
    cola=''
    for i in range(slots):
        x=330+i*40
        fill='#527A9E' if i<personas else '#DCE5ED'
        cola+=f'<circle cx="{x}" cy="151" r="9" fill="{fill}"/><rect x="{x-10}" y="163" width="20" height="24" rx="6" fill="{fill}"/>'
    extra='' if c<=6 else f'+ {c-6} lugares adicionales'
    html=f"""
    <html><body style="margin:0;background:#F7F9FC;font-family:Arial,sans-serif"><div style="background:#fff;border:1px solid #E1E8EF;border-radius:22px;padding:10px">
    <svg viewBox="0 0 1180 360" width="100%">
      <defs><marker id="arr1c" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#7B8EA3"/></marker></defs>
      <rect x="8" y="8" width="1164" height="344" rx="22" fill="#F3F8FC"/>
      <text x="40" y="48" font-size="24" font-weight="700" fill="#17324D">{titulo}</text>
      <text x="40" y="73" font-size="14" fill="#667085">Un servidor + c lugares de espera. La capacidad total es K = c + 1.</text>
      <rect x="35" y="105" width="205" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/><rect x="280" y="105" width="310" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/><rect x="650" y="105" width="235" height="155" rx="18" fill="#EAF7EF" stroke="#B7DDC5"/><rect x="940" y="105" width="205" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/>
      <line x1="240" y1="182" x2="275" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arr1c)"/><line x1="590" y1="182" x2="645" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arr1c)"/><line x1="885" y1="182" x2="935" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#arr1c)"/>
      <text x="138" y="155" text-anchor="middle" font-size="26">👥</text><text x="138" y="215" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Llegadas</text><text x="138" y="238" text-anchor="middle" font-size="12.5" fill="#667085">λ = {r['lambda']:.2f}/h</text>
      {cola}<text x="435" y="215" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Cola limitada</text><text x="435" y="237" text-anchor="middle" font-size="12.5" fill="#667085">c = {c} lugares · {extra}</text>
      <circle cx="768" cy="148" r="11" fill="#15803D"/><rect x="755" y="163" width="26" height="30" rx="7" fill="#15803D"/><text x="768" y="215" text-anchor="middle" font-size="17" font-weight="700" fill="#14532D">1 servidor</text><text x="768" y="238" text-anchor="middle" font-size="12.5" fill="#3F6B4F">μ = {r['mu']:.2f}/h</text>
      <circle cx="1042" cy="154" r="28" fill="#FDECEC" stroke="#F2C7C7"/><text x="1042" y="162" text-anchor="middle" font-size="25">↪</text><text x="1042" y="215" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Salida / rechazo</text><text x="1042" y="238" text-anchor="middle" font-size="12.5" fill="#667085">Bloqueo = {r['P_bloqueo']*100:.1f}%</text>
      <rect x="40" y="295" width="1095" height="40" rx="18" fill="#EAF1F7"/><text x="590" y="320" text-anchor="middle" font-size="14" font-weight="700" fill="#1F4E78">K = {r['K']} total · Cola media {r['Lq']:.2f} · Espera {r['Wq']*60:.1f} min · Aceptados {r['lambda_eff']:.2f}/h</text>
    </svg></div></body></html>"""
    components.html(html,height=405,scrolling=False)


def grafico_c(t_llegada,t_atencion,cmax=15):
    filas=[]
    for c in range(0,cmax+1):
        r=calcular_mm1c(t_llegada,t_atencion,c)
        filas.append({'c':c,'Bloqueo':r['P_bloqueo']*100})
    df=pd.DataFrame(filas)
    fig=go.Figure(go.Scatter(x=df['c'],y=df['Bloqueo'],mode='lines+markers',line=dict(width=4),marker=dict(size=8),hovertemplate='Lugares de espera: %{x}<br>Bloqueo: %{y:.2f}%<extra></extra>'))
    fig.update_layout(title='Cómo disminuye el rechazo cuando agregas lugares de espera',xaxis_title='Capacidad de la cola c',yaxis_title='Probabilidad de rechazo (%)',template='plotly_white',height=420,margin=dict(l=30,r=20,t=70,b=40))
    fig.update_xaxes(dtick=1)
    return fig


st.markdown("""<div class="hero"><div class="eyebrow">Modo Aprendizaje · Cola limitada</div><h1>08. Modelo M/M/1/c</h1><p>Aprende a analizar un sistema con un solo servidor y un número máximo de personas que pueden esperar. Cuando la fila se llena, nuevas llegadas son rechazadas.</p></div>""",unsafe_allow_html=True)

st.markdown('## 1. ¿Qué aprenderás?')
a,b,c,d=st.columns(4)
with a: st.markdown('<div class="card"><h4>🪑 Espera limitada</h4><p>Distinguir c lugares de espera de la capacidad total K.</p></div>',unsafe_allow_html=True)
with b: st.markdown('<div class="card"><h4>🚫 Rechazo</h4><p>Medir la probabilidad de que un cliente no pueda ingresar.</p></div>',unsafe_allow_html=True)
with c: st.markdown('<div class="card"><h4>🧪 Experimentar</h4><p>Agregar lugares de espera y observar qué cambia.</p></div>',unsafe_allow_html=True)
with d: st.markdown('<div class="card"><h4>💡 Decidir</h4><p>Equilibrar espacio físico, espera y clientes perdidos.</p></div>',unsafe_allow_html=True)

st.markdown('## 2. Visualiza la diferencia entre c y K')
r0=calcular_mm1c(30,20,4)
render_diagrama(r0,'Ejemplo visual · un servidor y cuatro lugares de espera')
st.markdown('<div class="warn"><b>Importante:</b> en este módulo <b>c</b> representa solo los lugares de espera. Como existe un servidor, la capacidad total es <b>K = c + 1</b>.</div>',unsafe_allow_html=True)

st.markdown('## 3. Cómo funciona el modelo')
st.markdown('Las llegadas son Poisson, el servicio es exponencial, existe un solo servidor y la cola admite como máximo c clientes esperando. Si servidor + cola están completos, el cliente que llega no ingresa.')
with st.expander('Ver formulación',expanded=False):
    st.latex(r'\rho=\frac{\lambda}{\mu}')
    st.latex(r'P_n=\frac{(1-\rho)\rho^n}{1-\rho^{K+1}}\quad (\rho\neq1)')
    st.latex(r'P_{bloqueo}=P_K\qquad ;\qquad \lambda_{ef}=\lambda(1-P_K)')
    st.caption('Cuando ρ = 1, los estados 0,...,K tienen probabilidad uniforme 1/(K+1).')

st.markdown('## 4. Ejemplo guiado')
st.markdown('<div class="example"><b>Situación:</b> llega un cliente cada 30 min, atenderlo toma 20 min y solo 4 personas pueden esperar.</div>',unsafe_allow_html=True)
e1,e2,e3,e4,e5=st.columns(5)
e1.metric('Carga nominal',f"{r0['rho_nominal']*100:.1f}%")
e2.metric('Bloqueo',f"{r0['P_bloqueo']*100:.2f}%")
e3.metric('Aceptados',f"{r0['lambda_eff']:.2f}/h")
e4.metric('Cola media',f"{r0['Lq']:.2f}")
e5.metric('Wq',f"{r0['Wq']*60:.1f} min")
st.info('La capacidad finita evita una cola infinita, pero parte de la demanda puede perderse cuando el sistema está lleno.')

st.markdown('## 5. Laboratorio interactivo')
x1,x2,x3=st.columns(3)
with x1: tl=st.slider('Llega 1 cliente cada... (min)',1.0,40.0,10.0,.5)
with x2: ta=st.slider('Atención promedio (min)',1.0,40.0,8.0,.5)
with x3: ccola=st.slider('Lugares disponibles en la cola (c)',0,15,4)
r=calcular_mm1c(tl,ta,ccola)
render_diagrama(r,'Tu escenario interactivo')
m1,m2,m3,m4,m5=st.columns(5)
m1.metric('K total',r['K']);m2.metric('Bloqueo',f"{r['P_bloqueo']*100:.2f}%");m3.metric('Prob. de esperar',f"{r['P_espera']*100:.1f}%");m4.metric('Wq',f"{r['Wq']*60:.1f} min");m5.metric('Aceptados',f"{r['lambda_eff']:.2f}/h")
st.plotly_chart(grafico_c(tl,ta,15),use_container_width=True)
st.caption('Más espacio para esperar reduce el rechazo, pero no acelera al servidor. La congestión puede desplazarse desde “clientes perdidos” hacia “clientes esperando”.')

# EDU_INTERPRETATION_MM1C
r_interpretacion = dict(r)
r_interpretacion.setdefault("s", 1)
r_interpretacion.setdefault("lambda_efectiva", r.get("lambda_eff", r.get("lambda", 0.0)))
st.markdown(to_markdown(interpret_mmsk(r_interpretacion), title="🧠 Interpretación de tu M/M/1 con espera limitada"))

st.markdown('## 6. Reto de destreza')
st.markdown('<div class="skill"><b>Reto:</b> llega un cliente cada 5 min y el servicio toma 4 min. Ajusta c hasta conseguir un bloqueo de 2 % o menos.</div>',unsafe_allow_html=True)
cr=st.slider('Lugares de espera para el reto',0,15,5,key='reto_mm1c')
rr=calcular_mm1c(5,4,cr)
r1,r2,r3=st.columns(3);r1.metric('c',cr);r2.metric('K total',rr['K']);r3.metric('Bloqueo',f"{rr['P_bloqueo']*100:.2f}%")
if rr['P_bloqueo']<=.02: st.success('✅ Reto logrado. La capacidad de espera seleccionada mantiene el bloqueo en 2 % o menos.')
else: st.warning('Todavía se pierde más del 2 % de las llegadas. Aumenta c y observa el cambio.')

st.markdown('## 7. Qué debes llevarte')
st.markdown('- **c** limita solo la cola; la capacidad total es **K = c + 1**.\n- Una cola finita introduce la probabilidad de **bloqueo/rechazo**.\n- La tasa efectiva de llegada es menor que la demanda original cuando hay rechazo.\n- Agregar espacio reduce bloqueo, pero no mejora la velocidad de servicio.\n- La decisión debe considerar simultáneamente espacio, espera y clientes perdidos.')
st.info('Siguiente paso: compara este caso con sistemas de varios servidores y capacidad total limitada.')
