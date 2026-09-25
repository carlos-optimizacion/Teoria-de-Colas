import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from interpretation_core import interpret_mmsk, to_markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="10 - M/M/s/c | Laboratorio", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.stApp{background:#F7F9FC}.block-container{padding-top:1.1rem;padding-bottom:2.6rem;max-width:1450px}
.hero{background:linear-gradient(135deg,#12324D 0%,#1F5A86 58%,#2D7BA8 100%);border-radius:24px;padding:30px 34px;color:white;box-shadow:0 16px 34px rgba(23,50,77,.16);margin-bottom:1rem}.hero h1{margin:0;font-size:2.15rem}.hero p{margin:.7rem 0 0;opacity:.94;max-width:1050px}.eyebrow{font-size:.76rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;opacity:.82}
.card{background:white;border:1px solid #E3E9F0;border-radius:16px;padding:18px 20px;box-shadow:0 5px 16px rgba(31,78,120,.05);min-height:128px}.card h4{margin:0 0 .45rem;color:#17324D}.card p{margin:0;color:#5A6675}
.example{background:#fff;border:1px solid #DDE5EC;border-left:6px solid #1F5A86;border-radius:16px;padding:18px 20px;margin:.5rem 0 1rem}.warn{background:#FFF7E6;border:1px solid #F0D9AB;border-left:6px solid #D97706;border-radius:14px;padding:16px 18px;margin:.45rem 0 1rem;color:#75440A}.skill{background:linear-gradient(135deg,#F0F6FB 0%,#FFFFFF 100%);border:1px solid #CDDFEC;border-radius:18px;padding:20px 22px;margin:.5rem 0 1rem}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E7EE;padding:14px 16px;border-radius:14px;box-shadow:0 4px 12px rgba(31,78,120,.04)}#MainMenu{visibility:hidden}footer{visibility:hidden}
</style>
""",unsafe_allow_html=True)


def calc(tl,ta,s,c):
    lam=60/tl; mu=60/ta; s=int(s); c=int(c)
    if c<s: raise ValueError('La capacidad total c debe ser mayor o igual al número de servidores.')
    pesos=[1.0]
    for n in range(1,c+1):
        pesos.append(pesos[-1]*lam/(min(n,s)*mu))
    z=sum(pesos); p=[x/z for x in pesos]
    pb=p[-1]; le=lam*(1-pb); L=sum(n*p[n] for n in range(c+1)); busy=le/mu; Lq=max(0,L-busy); W=L/le if le>0 else float('inf'); Wq=Lq/le if le>0 else float('inf'); util=busy/s
    return {'lambda':lam,'mu':mu,'s':s,'c':c,'P':p,'P_bloqueo':pb,'lambda_eff':le,'L':L,'Lq':Lq,'W':W,'Wq':Wq,'rho':util}


def render(r,titulo):
    espera=max(0,r['c']-r['s']); slots=min(6,espera); occ=min(slots,max(0,int(math.ceil(r['Lq'])))); cola=''
    for i in range(slots):
        x=335+i*38; fill='#527A9E' if i<occ else '#DCE5ED'; cola+=f'<circle cx="{x}" cy="152" r="9" fill="{fill}"/><rect x="{x-10}" y="164" width="20" height="24" rx="6" fill="{fill}"/>'
    serv=''; vis=min(4,r['s'])
    for i in range(vis):
        y=120+i*44; serv+=f'<rect x="690" y="{y}" width="180" height="34" rx="11" fill="#EAF7EF" stroke="#B7DDC5"/><text x="780" y="{y+22}" text-anchor="middle" font-size="13" font-weight="700" fill="#14532D">Servidor {i+1}</text>'
    html=f"""<html><body style="margin:0;background:#F7F9FC;font-family:Arial,sans-serif"><div style="background:#fff;border:1px solid #E1E8EF;border-radius:22px;padding:10px"><svg viewBox="0 0 1180 360" width="100%">
    <defs><marker id="ac" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#7B8EA3"/></marker></defs><rect x="8" y="8" width="1164" height="344" rx="22" fill="#F3F8FC"/>
    <text x="40" y="48" font-size="24" font-weight="700" fill="#17324D">{titulo}</text><text x="40" y="73" font-size="14" fill="#667085">Varios servidores y una capacidad total finita c.</text>
    <rect x="35" y="105" width="205" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/><rect x="280" y="105" width="300" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/><rect x="640" y="95" width="280" height="175" rx="18" fill="#fff" stroke="#DCE6EF"/><rect x="965" y="105" width="180" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/>
    <line x1="240" y1="182" x2="275" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#ac)"/><line x1="580" y1="182" x2="635" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#ac)"/><line x1="920" y1="182" x2="960" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#ac)"/>
    <text x="138" y="155" text-anchor="middle" font-size="26">👥</text><text x="138" y="215" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Llegadas</text><text x="138" y="238" text-anchor="middle" font-size="12.5" fill="#667085">λ={r['lambda']:.2f}/h</text>
    {cola}<text x="430" y="215" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Espera</text><text x="430" y="238" text-anchor="middle" font-size="12.5" fill="#667085">máx. {espera} esperando</text>
    {serv}<text x="780" y="294" text-anchor="middle" font-size="13" font-weight="700" fill="#17324D">{r['s']} servidor(es)</text>
    <circle cx="1055" cy="155" r="28" fill="#FDECEC" stroke="#F2C7C7"/><text x="1055" y="163" text-anchor="middle" font-size="24">↪</text><text x="1055" y="215" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Bloqueo</text><text x="1055" y="238" text-anchor="middle" font-size="12.5" fill="#667085">{r['P_bloqueo']*100:.1f}%</text>
    <rect x="40" y="300" width="1095" height="40" rx="18" fill="#EAF1F7"/><text x="590" y="325" text-anchor="middle" font-size="14" font-weight="700" fill="#1F4E78">c total={r['c']} · Utilización={r['rho']*100:.1f}% · Wq={r['Wq']*60:.1f} min · Aceptados={r['lambda_eff']:.2f}/h</text>
    </svg></div></body></html>"""
    components.html(html,height=405,scrolling=False)


def chart(tl,ta,s,cmax):
    rows=[]
    for c in range(s,cmax+1):
        r=calc(tl,ta,s,c); rows.append({'c':c,'Bloqueo':r['P_bloqueo']*100,'Wq':r['Wq']*60})
    df=pd.DataFrame(rows); fig=go.Figure(go.Scatter(x=df['c'],y=df['Bloqueo'],mode='lines+markers',line=dict(width=4),marker=dict(size=8),hovertemplate='Capacidad total: %{x}<br>Bloqueo: %{y:.2f}%<extra></extra>'))
    fig.update_layout(title='Efecto de ampliar la capacidad total',xaxis_title='Capacidad total c',yaxis_title='Probabilidad de bloqueo (%)',template='plotly_white',height=420,margin=dict(l=30,r=20,t=70,b=40)); fig.update_xaxes(dtick=1); return fig


st.markdown("""<div class="hero"><div class="eyebrow">Modo Aprendizaje · Capacidad total limitada</div><h1>10. Modelo M/M/s/c</h1><p>Analiza varios servidores cuando el sistema completo solo admite hasta c clientes entre atención y espera.</p></div>""",unsafe_allow_html=True)
st.markdown('<div class="warn"><b>Aclaración de notación:</b> este modelo es matemáticamente equivalente a M/M/s/K cuando <b>c</b> se usa para representar la capacidad total. En otros textos, c puede significar servidores; por eso aquí se explicita su significado.</div>',unsafe_allow_html=True)

st.markdown('## 1. ¿Qué aprenderás?')
a,b,c,d=st.columns(4)
with a: st.markdown('<div class="card"><h4>👥 Servidores</h4><p>Separar cantidad de servidores de capacidad total.</p></div>',unsafe_allow_html=True)
with b: st.markdown('<div class="card"><h4>🏠 Capacidad</h4><p>Interpretar c como máximo total dentro del sistema.</p></div>',unsafe_allow_html=True)
with c: st.markdown('<div class="card"><h4>🚫 Bloqueo</h4><p>Medir la pérdida de llegadas cuando el sistema se llena.</p></div>',unsafe_allow_html=True)
with d: st.markdown('<div class="card"><h4>💡 Decidir</h4><p>Evaluar si conviene ampliar espacio o capacidad de servicio.</p></div>',unsafe_allow_html=True)

st.markdown('## 2. Visualiza el sistema')
r0=calc(10,15,2,5); render(r0,'Ejemplo visual · 2 servidores y capacidad total c = 5')
st.markdown('Aquí pueden coexistir como máximo **5 clientes**: hasta 2 en servicio y hasta 3 esperando. El siguiente cliente que llegue cuando esos cinco lugares estén ocupados es bloqueado.')

with st.expander('Ver formulación',expanded=False):
    st.markdown('Se modela como un proceso nacimiento–muerte finito. El bloqueo es la probabilidad del último estado.')
    st.latex(r'P_{bloqueo}=P_c')
    st.latex(r'\lambda_{ef}=\lambda(1-P_c)')
    st.latex(r'W=\frac{L}{\lambda_{ef}}\qquad ;\qquad W_q=\frac{L_q}{\lambda_{ef}}')

st.markdown('## 3. Ejemplo guiado')
st.markdown('<div class="example"><b>Situación:</b> llega un cliente cada 10 min, cada atención tarda 15 min, hay 2 servidores y el sistema admite máximo 5 clientes.</div>',unsafe_allow_html=True)
e1,e2,e3,e4,e5=st.columns(5);e1.metric('Utilización',f"{r0['rho']*100:.1f}%");e2.metric('Bloqueo',f"{r0['P_bloqueo']*100:.2f}%");e3.metric('Aceptados',f"{r0['lambda_eff']:.2f}/h");e4.metric('Lq',f"{r0['Lq']:.2f}");e5.metric('Wq',f"{r0['Wq']*60:.1f} min")

st.markdown('## 4. Laboratorio interactivo')
x1,x2,x3,x4=st.columns(4)
with x1: tl=st.slider('Llega 1 cliente cada... (min)',1.0,30.0,10.0,.5)
with x2: ta=st.slider('Atención promedio (min)',1.0,30.0,15.0,.5)
with x3: s=st.slider('Servidores',1,8,2)
with x4: cap=st.slider('Capacidad total c',s,max(s,20),max(s,5))
r=calc(tl,ta,s,cap); render(r,'Tu escenario interactivo')
m1,m2,m3,m4,m5=st.columns(5);m1.metric('Utilización',f"{r['rho']*100:.1f}%");m2.metric('Bloqueo',f"{r['P_bloqueo']*100:.2f}%");m3.metric('Aceptados',f"{r['lambda_eff']:.2f}/h");m4.metric('Lq',f"{r['Lq']:.2f}");m5.metric('Wq',f"{r['Wq']*60:.1f} min")
st.plotly_chart(chart(tl,ta,s,min(20,max(cap+5,s+8))),use_container_width=True)

# EDU_INTERPRETATION_MMSC
r_interpretacion = dict(r)
r_interpretacion.setdefault("s", s)
r_interpretacion.setdefault("K", cap)
r_interpretacion.setdefault("lambda_efectiva", r.get("lambda_eff", r.get("lambda", 0.0)))
st.markdown(to_markdown(interpret_mmsk(r_interpretacion), title="🧠 Interpretación de tu sistema con capacidad total limitada"))

st.markdown('## 5. Reto de destreza')
st.markdown('<div class="skill"><b>Reto:</b> con llegadas cada 4 min, atención de 8 min y 3 servidores, encuentra una capacidad total que mantenga el bloqueo en 3 % o menos.</div>',unsafe_allow_html=True)
cr=st.slider('Capacidad total para el reto',3,18,6,key='reto_mmsc');rr=calc(4,8,3,cr);r1,r2,r3=st.columns(3);r1.metric('c total',cr);r2.metric('Bloqueo',f"{rr['P_bloqueo']*100:.2f}%");r3.metric('Wq',f"{rr['Wq']*60:.1f} min")
if rr['P_bloqueo']<=.03: st.success('✅ Reto logrado. La capacidad seleccionada mantiene el bloqueo en 3 % o menos.')
else: st.warning('El rechazo aún supera 3 %. Amplía la capacidad total y observa el efecto.')

st.markdown('## 6. Qué debes llevarte')
st.markdown('- Aquí **c representa capacidad total**, no número de servidores.\n- Matemáticamente es la misma lógica de M/M/s/K cuando K=c.\n- Un sistema finito convierte parte de la congestión en **bloqueo**.\n- La tasa efectiva de clientes atendibles disminuye cuando aumenta el rechazo.\n- Capacidad física y capacidad de servicio deben analizarse por separado.')
st.info('Siguiente paso: estudia el sistema sin cola, donde todos los lugares disponibles son servidores y cualquier llegada adicional se bloquea.')
