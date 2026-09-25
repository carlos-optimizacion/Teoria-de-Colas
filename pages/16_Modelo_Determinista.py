import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="16 - D/D/1 | Laboratorio", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.stApp{background:#F7F9FC}.block-container{padding-top:1.1rem;padding-bottom:2.6rem;max-width:1450px}
.hero{background:linear-gradient(135deg,#12324D 0%,#1F5A86 58%,#2D7BA8 100%);border-radius:24px;padding:30px 34px;color:white;box-shadow:0 16px 34px rgba(23,50,77,.16);margin-bottom:1rem}.hero h1{margin:0;font-size:2.15rem}.hero p{margin:.7rem 0 0;opacity:.94;max-width:1050px}.eyebrow{font-size:.76rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;opacity:.82}
.card{background:white;border:1px solid #E3E9F0;border-radius:16px;padding:18px 20px;box-shadow:0 5px 16px rgba(31,78,120,.05);min-height:128px}.card h4{margin:0 0 .45rem;color:#17324D}.card p{margin:0;color:#5A6675}
.example{background:#fff;border:1px solid #DDE5EC;border-left:6px solid #1F5A86;border-radius:16px;padding:18px 20px;margin:.5rem 0 1rem}.warn{background:#FFF7E6;border:1px solid #F0D9AB;border-left:6px solid #D97706;border-radius:14px;padding:16px 18px;margin:.45rem 0 1rem;color:#75440A}.skill{background:linear-gradient(135deg,#F0F6FB 0%,#FFFFFF 100%);border:1px solid #CDDFEC;border-radius:18px;padding:20px 22px;margin:.5rem 0 1rem}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E7EE;padding:14px 16px;border-radius:14px;box-shadow:0 4px 12px rgba(31,78,120,.04)}#MainMenu{visibility:hidden}footer{visibility:hidden}
</style>
""",unsafe_allow_html=True)


def simular(T,S,n=12):
    filas=[]; fin_anterior=0.0
    for i in range(1,n+1):
        llegada=(i-1)*T
        inicio=max(llegada,fin_anterior)
        fin=inicio+S
        espera=inicio-llegada
        filas.append({'Cliente':i,'Llegada':llegada,'Inicio servicio':inicio,'Fin servicio':fin,'Espera':espera})
        fin_anterior=fin
    rho=S/T
    return pd.DataFrame(filas),rho


def render(T,S,rho,titulo):
    if S<T: estado='Sin cola en operación ideal'; color='#15803D'; bg='#EAF7EF'; texto='El servidor termina antes de la siguiente llegada.'
    elif abs(S-T)<1e-12: estado='Sin holgura'; color='#D97706'; bg='#FFF7E6'; texto='Cada servicio termina exactamente cuando llega el siguiente cliente.'
    else: estado='Cola creciente'; color='#B42318'; bg='#FDECEC'; texto='Cada cliente llega antes de que termine el servicio anterior.'
    html=f"""<html><body style="margin:0;background:#F7F9FC;font-family:Arial,sans-serif"><div style="background:#fff;border:1px solid #E1E8EF;border-radius:22px;padding:10px"><svg viewBox="0 0 1180 350" width="100%">
    <defs><marker id="add" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#7B8EA3"/></marker></defs><rect x="8" y="8" width="1164" height="334" rx="22" fill="#F3F8FC"/>
    <text x="40" y="48" font-size="24" font-weight="700" fill="#17324D">{titulo}</text><text x="40" y="73" font-size="14" fill="#667085">Llegadas y servicios ocurren con tiempos constantes: no hay variabilidad aleatoria.</text>
    <rect x="50" y="105" width="250" height="145" rx="18" fill="#fff" stroke="#DCE6EF"/><rect x="370" y="105" width="250" height="145" rx="18" fill="#fff" stroke="#DCE6EF"/><rect x="690" y="105" width="250" height="145" rx="18" fill="#EAF7EF" stroke="#B7DDC5"/><rect x="995" y="105" width="140" height="145" rx="18" fill="#fff" stroke="#DCE6EF"/>
    <line x1="300" y1="178" x2="365" y2="178" stroke="#7B8EA3" stroke-width="4" marker-end="url(#add)"/><line x1="620" y1="178" x2="685" y2="178" stroke="#7B8EA3" stroke-width="4" marker-end="url(#add)"/><line x1="940" y1="178" x2="990" y2="178" stroke="#7B8EA3" stroke-width="4" marker-end="url(#add)"/>
    <text x="175" y="155" text-anchor="middle" font-size="30">⏱️</text><text x="175" y="208" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Llegada cada {T:.1f} min</text><text x="175" y="231" text-anchor="middle" font-size="12.5" fill="#667085">T constante</text>
    <text x="495" y="155" text-anchor="middle" font-size="30">🧍</text><text x="495" y="208" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Espera</text><text x="495" y="231" text-anchor="middle" font-size="12.5" fill="#667085">depende de S frente a T</text>
    <text x="815" y="155" text-anchor="middle" font-size="30">⚙️</text><text x="815" y="208" text-anchor="middle" font-size="17" font-weight="700" fill="#14532D">Servicio {S:.1f} min</text><text x="815" y="231" text-anchor="middle" font-size="12.5" fill="#3F6B4F">S constante</text>
    <text x="1065" y="160" text-anchor="middle" font-size="30">✅</text><text x="1065" y="208" text-anchor="middle" font-size="17" font-weight="700" fill="#17324D">Salida</text>
    <rect x="40" y="280" width="1095" height="40" rx="20" fill="{bg}"/><circle cx="65" cy="300" r="7" fill="{color}"/><text x="84" y="305" font-size="14" font-weight="700" fill="{color}">{estado}</text><text x="365" y="305" font-size="14" fill="#5B6675">ρ = S/T =</text><text x="445" y="305" font-size="14" font-weight="700" fill="#17324D">{rho:.2f}</text><text x="555" y="305" font-size="14" fill="#5B6675">{texto}</text>
    </svg></div></body></html>"""
    components.html(html,height=395,scrolling=False)


def grafico(df):
    fig=go.Figure(go.Scatter(x=df['Cliente'],y=df['Espera'],mode='lines+markers',line=dict(width=4),marker=dict(size=9),hovertemplate='Cliente %{x}<br>Espera %{y:.1f} min<extra></extra>'))
    fig.update_layout(title='Cómo evoluciona la espera cliente a cliente',xaxis_title='Cliente',yaxis_title='Espera antes de iniciar servicio (min)',template='plotly_white',height=420,margin=dict(l=30,r=20,t=70,b=40));fig.update_xaxes(dtick=1);return fig


st.markdown("""<div class="hero"><div class="eyebrow">Modo Aprendizaje · Sistema determinista</div><h1>16. Modelo D/D/1</h1><p>Observa qué ocurre cuando tanto las llegadas como los tiempos de servicio son completamente regulares. Este modelo muestra con claridad la diferencia entre capacidad y variabilidad.</p></div>""",unsafe_allow_html=True)

st.markdown('## 1. ¿Qué aprenderás?')
a,b,c,d=st.columns(4)
with a: st.markdown('<div class="card"><h4>⏱️ Sin variabilidad</h4><p>Reconocer un sistema con intervalos perfectamente constantes.</p></div>',unsafe_allow_html=True)
with b: st.markdown('<div class="card"><h4>⚖️ Comparar T y S</h4><p>Entender cuándo el servidor alcanza a terminar antes de la próxima llegada.</p></div>',unsafe_allow_html=True)
with c: st.markdown('<div class="card"><h4>📈 Observar</h4><p>Ver cómo crece la espera cuando S supera T.</p></div>',unsafe_allow_html=True)
with d: st.markdown('<div class="card"><h4>💡 Interpretar</h4><p>Distinguir congestión por capacidad de congestión por variabilidad.</p></div>',unsafe_allow_html=True)

st.markdown('## 2. La regla visual')
df0,rho0=simular(4,3,10);render(4,3,rho0,'Ejemplo visual · una llegada cada 4 min y servicio de 3 min')
st.markdown('<div class="warn"><b>En D/D/1 ideal:</b> si S ≤ T y el sistema inicia vacío, cada cliente puede comenzar servicio al llegar. Si S > T, cada atención tarda más que el intervalo entre llegadas y la espera aumenta cliente tras cliente.</div>',unsafe_allow_html=True)

st.markdown('## 3. Fórmulas básicas')
with st.expander('Ver relaciones',expanded=False):
    st.latex(r'\lambda=\frac{1}{T}\qquad ;\qquad \mu=\frac{1}{S}')
    st.latex(r'\rho=\frac{\lambda}{\mu}=\frac{S}{T}')
    st.caption('Si trabajas en minutos, λ y μ quedan en clientes por minuto. Para clientes/hora usa 60/T y 60/S.')

st.markdown('## 4. Ejemplo guiado')
st.markdown('<div class="example"><b>Situación:</b> una pieza llega exactamente cada 4 min y el proceso tarda exactamente 3 min por pieza.</div>',unsafe_allow_html=True)
e1,e2,e3,e4=st.columns(4);e1.metric('T', '4 min');e2.metric('S','3 min');e3.metric('Utilización',f'{rho0*100:.1f}%');e4.metric('Espera máxima',f"{df0['Espera'].max():.1f} min")
st.success('Como S < T, el servidor termina cada pieza antes de que llegue la siguiente. En este escenario ideal no se forma cola.')

st.markdown('## 5. Laboratorio interactivo')
x1,x2,x3=st.columns(3)
with x1: T=st.slider('Intervalo entre llegadas T (min)',1.0,15.0,4.0,.5)
with x2: S=st.slider('Tiempo de servicio S (min)',1.0,15.0,3.0,.5)
with x3: n=st.slider('Clientes a observar',5,25,12)
df,rho=simular(T,S,n);render(T,S,rho,'Tu escenario determinista')
m1,m2,m3,m4=st.columns(4);m1.metric('Utilización',f'{rho*100:.1f}%');m2.metric('Espera cliente 1',f"{df.iloc[0]['Espera']:.1f} min");m3.metric(f'Espera cliente {n}',f"{df.iloc[-1]['Espera']:.1f} min");m4.metric('Espera promedio',f"{df['Espera'].mean():.1f} min")
st.plotly_chart(grafico(df),use_container_width=True)
with st.expander('Ver cronograma de los primeros clientes'):
    st.dataframe(df,use_container_width=True,hide_index=True)

st.markdown('## 6. Reto de destreza')
st.markdown('<div class="skill"><b>Reto:</b> las piezas llegan exactamente cada 5 min. Ajusta el tiempo de proceso para que los primeros 15 clientes tengan espera cero.</div>',unsafe_allow_html=True)
Sr=st.slider('Tiempo de servicio para el reto (min)',1.0,8.0,6.0,.5,key='reto_dd1');dfr,rhor=simular(5,Sr,15);r1,r2,r3=st.columns(3);r1.metric('S',f'{Sr:.1f} min');r2.metric('ρ',f'{rhor*100:.1f}%');r3.metric('Espera máxima',f"{dfr['Espera'].max():.1f} min")
if dfr['Espera'].max()==0: st.success('✅ Reto logrado. El tiempo de servicio no supera el intervalo entre llegadas, por lo que no se acumula espera.')
else: st.warning('Aún se genera cola. Reduce S hasta que el servidor termine antes o exactamente al llegar el siguiente cliente.')

st.markdown('## 7. Qué debes llevarte')
st.markdown('- D/D/1 elimina la variabilidad de llegadas y servicio.\n- Si **S ≤ T** y el sistema parte vacío, la operación ideal puede funcionar sin cola.\n- Si **S > T**, la espera crece de forma acumulativa.\n- Comparar D/D/1 con M/M/1 muestra cuánto impacto puede tener la variabilidad.\n- Un proceso sincronizado puede alcanzar altos niveles de utilización sin generar la misma congestión que un sistema aleatorio.')
st.info('Con esto cierras los modelos fundamentales y puedes pasar a los casos aplicados, comparación de alternativas y Modo Analista.')
