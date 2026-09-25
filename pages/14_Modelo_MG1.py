import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="14 - M/G/1 | Laboratorio", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.stApp{background:#F7F9FC}.block-container{padding-top:1.1rem;padding-bottom:2.6rem;max-width:1450px}
.hero{background:linear-gradient(135deg,#12324D 0%,#1F5A86 58%,#2D7BA8 100%);border-radius:24px;padding:30px 34px;color:white;box-shadow:0 16px 34px rgba(23,50,77,.16);margin-bottom:1rem}.hero h1{margin:0;font-size:2.15rem}.hero p{margin:.7rem 0 0;opacity:.94;max-width:1050px}.eyebrow{font-size:.76rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;opacity:.82}
.card{background:white;border:1px solid #E3E9F0;border-radius:16px;padding:18px 20px;box-shadow:0 5px 16px rgba(31,78,120,.05);min-height:128px}.card h4{margin:0 0 .45rem;color:#17324D}.card p{margin:0;color:#5A6675}
.example{background:#fff;border:1px solid #DDE5EC;border-left:6px solid #1F5A86;border-radius:16px;padding:18px 20px;margin:.5rem 0 1rem}.warn{background:#FFF7E6;border:1px solid #F0D9AB;border-left:6px solid #D97706;border-radius:14px;padding:16px 18px;margin:.45rem 0 1rem;color:#75440A}.skill{background:linear-gradient(135deg,#F0F6FB 0%,#FFFFFF 100%);border:1px solid #CDDFEC;border-radius:18px;padding:20px 22px;margin:.5rem 0 1rem}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E7EE;padding:14px 16px;border-radius:14px;box-shadow:0 4px 12px rgba(31,78,120,.04)}#MainMenu{visibility:hidden}footer{visibility:hidden}
</style>
""",unsafe_allow_html=True)


def calcular_mg1(t_llegada_min,media_servicio_min,cv):
    lam=1.0/t_llegada_min
    ES=media_servicio_min
    var=(cv*ES)**2
    rho=lam*ES
    if rho>=1:
        return {'estable':False,'lambda_min':lam,'ES':ES,'cv':cv,'var':var,'rho':rho,'Lq':float('inf'),'Wq':float('inf'),'W':float('inf'),'L':float('inf')}
    ES2=var+ES**2
    Wq=lam*ES2/(2*(1-rho))
    Lq=lam*Wq
    W=Wq+ES
    L=lam*W
    return {'estable':True,'lambda_min':lam,'ES':ES,'cv':cv,'var':var,'rho':rho,'Lq':Lq,'Wq':Wq,'W':W,'L':L}


def render(r,titulo):
    estable=r['estable']; color='#15803D' if estable else '#B42318'; bg='#EAF7EF' if estable else '#FDECEC'; estado='Sistema estable' if estable else 'Capacidad insuficiente'; wq='∞' if not estable else f"{r['Wq']:.1f} min"
    nivel='Baja' if r['cv']<0.5 else ('Media' if r['cv']<1.0 else ('Alta' if r['cv']<1.5 else 'Muy alta'))
    html=f"""<html><body style="margin:0;background:#F7F9FC;font-family:Arial,sans-serif"><div style="background:#fff;border:1px solid #E1E8EF;border-radius:22px;padding:10px"><svg viewBox="0 0 1180 360" width="100%">
    <defs><marker id="amg" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#7B8EA3"/></marker></defs><rect x="8" y="8" width="1164" height="344" rx="22" fill="#F3F8FC"/>
    <text x="40" y="48" font-size="24" font-weight="700" fill="#17324D">{titulo}</text><text x="40" y="73" font-size="14" fill="#667085">Un servidor, llegadas aleatorias y tiempos de servicio con variabilidad general.</text>
    <rect x="40" y="105" width="205" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/><rect x="290" y="105" width="285" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/><rect x="635" y="105" width="250" height="155" rx="18" fill="#EAF7EF" stroke="#B7DDC5"/><rect x="940" y="105" width="205" height="155" rx="18" fill="#fff" stroke="#DCE6EF"/>
    <line x1="245" y1="182" x2="285" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#amg)"/><line x1="575" y1="182" x2="630" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#amg)"/><line x1="885" y1="182" x2="935" y2="182" stroke="#7B8EA3" stroke-width="4" marker-end="url(#amg)"/>
    <text x="142" y="153" text-anchor="middle" font-size="26">👥</text><text x="142" y="215" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Llegadas M</text><text x="142" y="238" text-anchor="middle" font-size="12.5" fill="#667085">cada {1/r['lambda_min']:.1f} min</text>
    <text x="432" y="150" text-anchor="middle" font-size="28">🧍🧍🧍</text><text x="432" y="215" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Cola</text><text x="432" y="238" text-anchor="middle" font-size="12.5" fill="#667085">Wq = {wq}</text>
    <text x="760" y="145" text-anchor="middle" font-size="28">👤</text><text x="760" y="195" text-anchor="middle" font-size="17" font-weight="700" fill="#14532D">Servicio G</text><text x="760" y="218" text-anchor="middle" font-size="12.5" fill="#3F6B4F">media={r['ES']:.1f} min</text><text x="760" y="239" text-anchor="middle" font-size="12.5" fill="#3F6B4F">CV={r['cv']:.2f} · {nivel}</text>
    <circle cx="1042" cy="154" r="28" fill="#EAF7EF" stroke="#A9D8BA"/><path d="M1029 154 L1039 164 L1057 142" fill="none" stroke="#15803D" stroke-width="6"/><text x="1042" y="215" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Salida</text>
    <rect x="40" y="295" width="250" height="40" rx="20" fill="{bg}"/><circle cx="63" cy="315" r="7" fill="{color}"/><text x="82" y="320" font-size="14" font-weight="700" fill="{color}">{estado}</text><text x="350" y="320" font-size="14" fill="#5B6675">Utilización:</text><text x="430" y="320" font-size="14" font-weight="700" fill="#17324D">{r['rho']*100:.1f}%</text><text x="540" y="320" font-size="14" fill="#5B6675">Variabilidad del servicio:</text><text x="700" y="320" font-size="14" font-weight="700" fill="#17324D">{nivel}</text>
    </svg></div></body></html>"""
    components.html(html,height=405,scrolling=False)


def chart_cv(tl,media,cv_actual):
    rows=[]
    for i in range(0,201,5):
        cv=i/100; r=calcular_mg1(tl,media,cv)
        rows.append({'CV':cv,'Wq':r['Wq'] if r['estable'] else None})
    df=pd.DataFrame(rows); fig=go.Figure(go.Scatter(x=df['CV'],y=df['Wq'],mode='lines',line=dict(width=4),hovertemplate='CV: %{x:.2f}<br>Wq: %{y:.1f} min<extra></extra>'))
    ract=calcular_mg1(tl,media,cv_actual)
    if ract['estable']: fig.add_trace(go.Scatter(x=[cv_actual],y=[ract['Wq']],mode='markers+text',text=['Escenario'],textposition='top center',marker=dict(size=13),showlegend=False))
    fig.update_layout(title='La variabilidad puede aumentar la espera aunque el promedio no cambie',xaxis_title='Coeficiente de variación del servicio (CV)',yaxis_title='Espera promedio Wq (min)',template='plotly_white',height=420,margin=dict(l=30,r=20,t=70,b=40));return fig


st.markdown("""<div class="hero"><div class="eyebrow">Modo Aprendizaje · Variabilidad del servicio</div><h1>14. Modelo M/G/1</h1><p>Descubre por qué dos procesos con el mismo tiempo promedio de atención pueden generar colas muy distintas cuando la variabilidad del servicio cambia.</p></div>""",unsafe_allow_html=True)

st.markdown('## 1. ¿Qué aprenderás?')
a,b,c,d=st.columns(4)
with a: st.markdown('<div class="card"><h4>🎲 Variabilidad</h4><p>Entender que el promedio del servicio no cuenta toda la historia.</p></div>',unsafe_allow_html=True)
with b: st.markdown('<div class="card"><h4>📏 CV</h4><p>Usar el coeficiente de variación para representar dispersión del servicio.</p></div>',unsafe_allow_html=True)
with c: st.markdown('<div class="card"><h4>🧪 Experimentar</h4><p>Mantener la media y cambiar solo la variabilidad.</p></div>',unsafe_allow_html=True)
with d: st.markdown('<div class="card"><h4>💡 Mejorar</h4><p>Reconocer que estandarizar procesos también reduce espera.</p></div>',unsafe_allow_html=True)

st.markdown('## 2. Qué significa M/G/1')
r0=calcular_mg1(6,4,.75);render(r0,'Ejemplo visual · mismo servidor, servicio variable')
st.markdown('**M**: llegadas Poisson / tiempos entre llegadas exponenciales. **G**: el tiempo de servicio puede seguir una distribución general. **1**: existe un solo servidor.')
st.markdown('<div class="warn"><b>Idea clave:</b> en M/G/1 la espera depende no solo del tiempo medio de servicio, sino también de su variabilidad. Reducir variación puede mejorar la experiencia sin contratar otro servidor.</div>',unsafe_allow_html=True)

st.markdown('## 3. Fórmula de Pollaczek–Khinchine')
with st.expander('Ver fórmula y significado',expanded=False):
    st.latex(r'\rho=\lambda E[S]')
    st.latex(r'W_q=\frac{\lambda E[S^2]}{2(1-\rho)}')
    st.latex(r'E[S^2]=Var(S)+E[S]^2')
    st.latex(r'L_q=\lambda W_q\qquad ;\qquad W=W_q+E[S]')
    st.caption('CV = desviación estándar / media. Por tanto Var(S) = (CV × E[S])².')

st.markdown('## 4. Ejemplo guiado')
st.markdown('<div class="example"><b>Situación:</b> llega un cliente cada 6 min, el servicio dura 4 min en promedio y el CV del servicio es 0.75.</div>',unsafe_allow_html=True)
e1,e2,e3,e4,e5=st.columns(5);e1.metric('Utilización',f"{r0['rho']*100:.1f}%");e2.metric('CV',f"{r0['cv']:.2f}");e3.metric('Lq',f"{r0['Lq']:.2f}");e4.metric('Wq',f"{r0['Wq']:.1f} min");e5.metric('W total',f"{r0['W']:.1f} min")
st.info('Si mantienes llegada y servicio medio constantes, cambiar únicamente el CV modifica la espera. Esa es la principal lección de M/G/1.')

st.markdown('## 5. Laboratorio interactivo')
x1,x2,x3=st.columns(3)
with x1: tl=st.slider('Llega 1 cliente cada... (min)',1.0,20.0,6.0,.5)
with x2: ms=st.slider('Servicio medio (min)',1.0,20.0,4.0,.5)
with x3: cv=st.slider('Coeficiente de variación CV',0.0,2.0,.75,.05)
r=calcular_mg1(tl,ms,cv);render(r,'Tu escenario interactivo')
if not r['estable']:
    st.error('La demanda iguala o supera la capacidad promedio del servidor. Reduce el tiempo de servicio o disminuye la tasa de llegada.')
else:
    m1,m2,m3,m4,m5=st.columns(5);m1.metric('Utilización',f"{r['rho']*100:.1f}%");m2.metric('CV',f"{cv:.2f}");m3.metric('Lq',f"{r['Lq']:.2f}");m4.metric('Wq',f"{r['Wq']:.1f} min");m5.metric('W',f"{r['W']:.1f} min")
st.plotly_chart(chart_cv(tl,ms,cv),use_container_width=True)
st.caption('CV = 0 representa un servicio perfectamente constante; CV = 1 tiene la misma variabilidad relativa de un servicio exponencial. Valores mayores implican mayor dispersión.')

st.markdown('## 6. Reto de destreza')
st.markdown('<div class="skill"><b>Reto:</b> llegan clientes cada 6 min y el servicio medio es 4 min. Reduce únicamente el CV hasta conseguir Wq ≤ 6 min.</div>',unsafe_allow_html=True)
cvr=st.slider('CV para el reto',0.0,1.8,1.0,.05,key='reto_mg1');rr=calcular_mg1(6,4,cvr)
r1,r2,r3=st.columns(3);r1.metric('CV',f"{cvr:.2f}");r2.metric('Utilización',f"{rr['rho']*100:.1f}%");r3.metric('Wq',f"{rr['Wq']:.2f} min" if rr['estable'] else '∞')
if rr['estable'] and rr['Wq']<=6: st.success('✅ Reto logrado. Mejoraste el nivel de servicio reduciendo variabilidad, sin cambiar el tiempo promedio de atención.')
else: st.warning('Aún no se cumple la meta. Reduce la variabilidad del servicio y observa cómo cae Wq.')

st.markdown('## 7. Qué debes llevarte')
st.markdown('- El promedio de servicio no es suficiente: la **variabilidad importa**.\n- M/G/1 utiliza E[S²], por lo que una mayor dispersión aumenta la espera.\n- CV permite comparar variabilidad en una escala relativa.\n- Estandarizar un proceso puede reducir colas sin aumentar capacidad.\n- La mejora operacional puede venir de velocidad, capacidad o reducción de variabilidad.')
st.info('Siguiente paso: D/D/1 para observar el extremo opuesto: un sistema sin variabilidad en llegadas ni servicio.')
