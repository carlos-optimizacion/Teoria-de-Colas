import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="12 - M/M/c/c | Laboratorio", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.stApp{background:#F7F9FC}.block-container{padding-top:1.1rem;padding-bottom:2.6rem;max-width:1450px}
.hero{background:linear-gradient(135deg,#12324D 0%,#1F5A86 58%,#2D7BA8 100%);border-radius:24px;padding:30px 34px;color:white;box-shadow:0 16px 34px rgba(23,50,77,.16);margin-bottom:1rem}.hero h1{margin:0;font-size:2.15rem}.hero p{margin:.7rem 0 0;opacity:.94;max-width:1050px}.eyebrow{font-size:.76rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;opacity:.82}
.card{background:white;border:1px solid #E3E9F0;border-radius:16px;padding:18px 20px;box-shadow:0 5px 16px rgba(31,78,120,.05);min-height:128px}.card h4{margin:0 0 .45rem;color:#17324D}.card p{margin:0;color:#5A6675}
.example{background:#fff;border:1px solid #DDE5EC;border-left:6px solid #1F5A86;border-radius:16px;padding:18px 20px;margin:.5rem 0 1rem}.warn{background:#FFF7E6;border:1px solid #F0D9AB;border-left:6px solid #D97706;border-radius:14px;padding:16px 18px;margin:.45rem 0 1rem;color:#75440A}.skill{background:linear-gradient(135deg,#F0F6FB 0%,#FFFFFF 100%);border:1px solid #CDDFEC;border-radius:18px;padding:20px 22px;margin:.5rem 0 1rem}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E7EE;padding:14px 16px;border-radius:14px;box-shadow:0 4px 12px rgba(31,78,120,.04)}#MainMenu{visibility:hidden}footer{visibility:hidden}
</style>
""",unsafe_allow_html=True)


def erlang_b(A,c):
    b=1.0
    for i in range(1,int(c)+1):
        b=(A*b)/(i+A*b)
    return b


def calcular(tl,ta,c):
    lam=60.0/tl; mu=60.0/ta; c=int(c); A=lam/mu; B=erlang_b(A,c); lam_eff=lam*(1-B); carried=A*(1-B); ocup=carried/c if c>0 else 0
    return {'lambda':lam,'mu':mu,'c':c,'A':A,'B':B,'lambda_eff':lam_eff,'carried':carried,'ocupacion':ocup,'Wq':0.0,'W':1/mu}


def render(r,titulo):
    c=r['c']; vis=min(6,c); serv=''
    xs=[650,760,870]; ys=[125,205]
    for i in range(vis):
        x=xs[i%3]; y=ys[i//3]; serv+=f'<rect x="{x}" y="{y}" width="95" height="58" rx="13" fill="#EAF7EF" stroke="#B7DDC5"/><text x="{x+47}" y="{y+24}" text-anchor="middle" font-size="13" font-weight="700" fill="#14532D">Servidor {i+1}</text><text x="{x+47}" y="{y+43}" text-anchor="middle" font-size="11" fill="#3F6B4F">μ={r["mu"]:.1f}/h</text>'
    extra='' if c<=6 else f'+ {c-6} servidores'
    html=f"""<html><body style="margin:0;background:#F7F9FC;font-family:Arial,sans-serif"><div style="background:#fff;border:1px solid #E1E8EF;border-radius:22px;padding:10px"><svg viewBox="0 0 1180 365" width="100%">
    <defs><marker id="ab" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#7B8EA3"/></marker></defs><rect x="8" y="8" width="1164" height="349" rx="22" fill="#F3F8FC"/>
    <text x="40" y="48" font-size="24" font-weight="700" fill="#17324D">{titulo}</text><text x="40" y="73" font-size="14" fill="#667085">No existe sala de espera: entrar significa recibir servicio; si todos están ocupados, la llegada se bloquea.</text>
    <rect x="40" y="105" width="210" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/><rect x="320" y="105" width="230" height="155" rx="18" fill="#FFF7E6" stroke="#F0D9AB"/><rect x="620" y="95" width="360" height="185" rx="18" fill="#fff" stroke="#DCE6EF"/><rect x="1010" y="105" width="130" height="155" rx="18" fill="#FDECEC" stroke="#F2C7C7"/>
    <line x1="250" y1="182" x2="315" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#ab)"/><line x1="550" y1="182" x2="615" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#ab)"/>
    <text x="145" y="150" text-anchor="middle" font-size="27">👥</text><text x="145" y="215" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Llegadas</text><text x="145" y="238" text-anchor="middle" font-size="12.5" fill="#667085">λ={r['lambda']:.2f}/h</text>
    <text x="435" y="150" text-anchor="middle" font-size="28">🚫</text><text x="435" y="205" text-anchor="middle" font-size="17" font-weight="700" fill="#75440A">Sin cola</text><text x="435" y="228" text-anchor="middle" font-size="12.5" fill="#75440A">0 lugares de espera</text>
    {serv}<text x="800" y="304" text-anchor="middle" font-size="13" font-weight="700" fill="#17324D">{c} servidor(es) · {extra}</text>
    <text x="1075" y="150" text-anchor="middle" font-size="28">↪</text><text x="1075" y="205" text-anchor="middle" font-size="16" font-weight="700" fill="#8A1C15">Bloqueo</text><text x="1075" y="228" text-anchor="middle" font-size="12.5" fill="#8A1C15">{r['B']*100:.1f}%</text>
    <rect x="40" y="310" width="1095" height="40" rx="18" fill="#EAF1F7"/><text x="590" y="335" text-anchor="middle" font-size="14" font-weight="700" fill="#1F4E78">Carga ofrecida A={r['A']:.2f} Erlangs · Ocupación media={r['ocupacion']*100:.1f}% · Aceptados={r['lambda_eff']:.2f}/h</text>
    </svg></div></body></html>"""
    components.html(html,height=410,scrolling=False)


def chart(tl,ta,cmax=12):
    rows=[]
    for c in range(1,cmax+1):
        r=calcular(tl,ta,c); rows.append({'Servidores':c,'Bloqueo':r['B']*100})
    df=pd.DataFrame(rows); fig=go.Figure(go.Scatter(x=df['Servidores'],y=df['Bloqueo'],mode='lines+markers',line=dict(width=4),marker=dict(size=8),hovertemplate='Servidores: %{x}<br>Bloqueo: %{y:.2f}%<extra></extra>'))
    fig.update_layout(title='Probabilidad de bloqueo según número de servidores',xaxis_title='Servidores disponibles',yaxis_title='Bloqueo (%)',template='plotly_white',height=420,margin=dict(l=30,r=20,t=70,b=40));fig.update_xaxes(dtick=1);return fig


st.markdown("""<div class="hero"><div class="eyebrow">Modo Aprendizaje · Sistema sin cola</div><h1>12. Modelo M/M/c/c · Erlang B</h1><p>Aprende a dimensionar sistemas donde no se permite esperar. Si todos los servidores están ocupados, la nueva llegada se pierde.</p></div>""",unsafe_allow_html=True)

st.markdown('## 1. ¿Qué aprenderás?')
a,b,c,d=st.columns(4)
with a: st.markdown('<div class="card"><h4>🚫 Sin espera</h4><p>Comprender la diferencia entre congestión con cola y congestión con bloqueo.</p></div>',unsafe_allow_html=True)
with b: st.markdown('<div class="card"><h4>📦 Carga</h4><p>Interpretar A = λ/μ como tráfico ofrecido en Erlangs.</p></div>',unsafe_allow_html=True)
with c: st.markdown('<div class="card"><h4>🧪 Dimensionar</h4><p>Cambiar el número de servidores y observar el bloqueo.</p></div>',unsafe_allow_html=True)
with d: st.markdown('<div class="card"><h4>💡 Decidir</h4><p>Elegir capacidad para alcanzar un nivel de pérdida aceptable.</p></div>',unsafe_allow_html=True)

st.markdown('## 2. Visualiza un sistema sin cola')
r0=calcular(12,30,4);render(r0,'Ejemplo visual · cuatro servidores sin sala de espera')
st.markdown('<div class="warn"><b>Idea clave:</b> aquí Wq = 0 para los clientes admitidos, porque nadie espera. El indicador crítico no es la espera: es la <b>probabilidad de bloqueo</b>.</div>',unsafe_allow_html=True)

st.markdown('## 3. Fórmula de Erlang B')
with st.expander('Ver formulación',expanded=False):
    st.latex(r'A=\frac{\lambda}{\mu}')
    st.latex(r'B(c,A)=\frac{A^c/c!}{\sum_{n=0}^{c}A^n/n!}')
    st.latex(r'\lambda_{ef}=\lambda(1-B)')
    st.caption('La aplicación calcula Erlang B de forma recursiva para mayor estabilidad numérica.')

st.markdown('## 4. Ejemplo guiado')
st.markdown('<div class="example"><b>Situación:</b> llega un cliente cada 12 min, cada servicio dura 30 min y existen 4 servidores. No hay sala de espera.</div>',unsafe_allow_html=True)
e1,e2,e3,e4=st.columns(4);e1.metric('Carga A',f"{r0['A']:.2f} Erlangs");e2.metric('Bloqueo',f"{r0['B']*100:.2f}%");e3.metric('Aceptados',f"{r0['lambda_eff']:.2f}/h");e4.metric('Ocupación media',f"{r0['ocupacion']*100:.1f}%")
st.info('La ocupación puede ser moderada y aun existir bloqueo porque las llegadas son aleatorias y pueden coincidir cuando todos los servidores están ocupados.')

st.markdown('## 5. Laboratorio interactivo')
x1,x2,x3=st.columns(3)
with x1: tl=st.slider('Llega 1 cliente cada... (min)',1.0,40.0,12.0,.5)
with x2: ta=st.slider('Duración del servicio (min)',1.0,60.0,30.0,.5)
with x3: cs=st.slider('Servidores disponibles',1,15,4)
r=calcular(tl,ta,cs);render(r,'Tu escenario interactivo')
m1,m2,m3,m4=st.columns(4);m1.metric('Carga A',f"{r['A']:.2f}");m2.metric('Bloqueo',f"{r['B']*100:.2f}%");m3.metric('Aceptados',f"{r['lambda_eff']:.2f}/h");m4.metric('Ocupación',f"{r['ocupacion']*100:.1f}%")
st.plotly_chart(chart(tl,ta,15),use_container_width=True)
st.caption('Cada servidor adicional reduce el bloqueo, pero el beneficio marginal disminuye. El objetivo es encontrar la capacidad necesaria para el nivel de pérdida permitido.')

st.markdown('## 6. Reto de destreza')
st.markdown('<div class="skill"><b>Reto:</b> llegan solicitudes cada 5 min y cada servicio dura 15 min. Encuentra el menor número de servidores que logra un bloqueo de 5 % o menos.</div>',unsafe_allow_html=True)
cr=st.slider('Servidores para el reto',1,12,3,key='reto_erlangb');rr=calcular(5,15,cr);r1,r2,r3=st.columns(3);r1.metric('Servidores',cr);r2.metric('Bloqueo',f"{rr['B']*100:.2f}%");r3.metric('Aceptados',f"{rr['lambda_eff']:.2f}/h")
if rr['B']<=.05:
    prev=calcular(5,15,cr-1)['B'] if cr>1 else 1
    if cr==1 or prev>.05: st.success('✅ Reto logrado y además encontraste la dotación mínima que cumple el 5 %.')
    else: st.info('Cumples la meta, pero prueba reducir un servidor: quizá exista una solución menor que también cumpla.')
else: st.warning('El bloqueo todavía supera 5 %. Aumenta la cantidad de servidores.')

st.markdown('## 7. Qué debes llevarte')
st.markdown('- En M/M/c/c **no existe cola**.\n- La congestión se expresa como **clientes bloqueados**, no como tiempo de espera.\n- Erlang B relaciona carga ofrecida y cantidad de servidores.\n- Más servidores disminuyen el bloqueo, pero con rendimientos marginales decrecientes.\n- El dimensionamiento busca el menor número de servidores que cumpla el nivel de pérdida aceptable.')
st.info('Siguiente paso: M/G/1, donde volverás a un solo servidor pero estudiarás cómo la variabilidad del tiempo de servicio cambia la espera.')
