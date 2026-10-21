from __future__ import annotations
import json, math, sys, time
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT=Path(__file__).resolve().parent
DJANGO_APP=ROOT/"django_app"
if str(DJANGO_APP) not in sys.path:
    sys.path.insert(0,str(DJANGO_APP))

from portal.challenge_engine import SCENARIOS, evaluate_game
from portal.network_engine import simulate_network
from queue_core import (
    mms_from_minutes,mmsk_from_minutes,mg1_from_minutes,dd1_sequence,
    economic_cost,evaluate_mms_capacity,recommend_mms_capacity,erlang_b
)

st.set_page_config(page_title="Decision Lab 2.0",page_icon="◈",layout="wide",initial_sidebar_state="expanded")

SCENE_DIR=DJANGO_APP/"static"/"img"/"scenarios"
MODELS=["M/M/1","M/M/s","M/M/s/K","M/M/1/c","M/M/s/c","Erlang B","M/G/1","D/D/1"]

def metric_cards(items,columns=4):
    cards=[]
    for label,value,kind in items:
        cards.append(f'<div class="kpi-card {kind}"><small>{label}</small><b>{value}</b></div>')
    st.markdown(f'<div class="kpi-grid cols-{columns}">'+"".join(cards)+'</div>',unsafe_allow_html=True)

def progress_html(value,label):
    pct=max(0,min(100,float(value)*100))
    st.markdown(f'<div class="dl-progress"><div class="dl-progress-head"><span>{label}</span><b>{pct:.0f}%</b></div><div class="dl-progress-track"><i style="width:{pct:.1f}%"></i></div></div>',unsafe_allow_html=True)

def css():
    st.markdown("""
    <style>
    .stApp{background:#F5F8FB;color:#12324F}.block-container{padding-top:.5rem;max-width:1600px}
    section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0B2D4F,#08243F);color:white}
    section[data-testid="stSidebar"] *{color:#EAF5FF}
    .dl-top{display:flex;justify-content:space-between;align-items:center;background:white;border:1px solid #DDE8F0;border-radius:16px;padding:12px 16px;margin-bottom:10px}
    .dl-brand{font-size:1.35rem;font-weight:900;color:#0F3E67}.dl-brand small{display:block;font-size:.72rem;font-weight:600;color:#70849A}
    .scene-card{background:white;border:2px solid #DCE8EF;border-radius:14px;overflow:hidden}.scene-card.selected{border-color:#1F83E1;box-shadow:0 0 0 3px #C8E3FC}
    .scene-caption{padding:8px 10px;font-weight:850;color:#153B63}.scene-caption small{display:block;color:#657C91;font-weight:500}
    .sim-head{display:flex;justify-content:space-between;gap:12px;align-items:center;background:#fff;border:1px solid #DDE8EF;border-radius:14px 14px 0 0;padding:12px 15px}
    .sim-head h2{font-size:1.2rem;margin:0;color:#103D66}.sim-head p{margin:2px 0 0;font-size:.78rem;color:#657C91}
    .facility{background:linear-gradient(180deg,#EEF6F8,#DCEBEF);border-left:1px solid #DDE8EF;border-right:1px solid #DDE8EF;padding:10px 14px}
    .facility-grid{display:grid;grid-template-columns:1fr 2fr;gap:12px}
    .zone{background:#FFFFFFE8;border:1px solid #CDDFE8;border-radius:12px;padding:10px;min-height:200px}
    .zone-title{font-size:.72rem;font-weight:900;color:#3A6078;letter-spacing:.05em}.queue-people,.servers{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
    .client{display:inline-grid;place-items:center;width:31px;height:31px;border-radius:50%;background:#A9D9F6;border:2px solid white;box-shadow:0 3px 7px #315D7440;font-size:.65rem;font-weight:900;color:#104669}
    .client.serving{background:#9AE3BC}.station{display:flex;flex-direction:column;gap:4px;align-items:center;min-width:96px;padding:8px;border-radius:10px;border:2px solid #94CAB7;background:#ECF8F2;font-size:.68rem}.station.busy{background:#E5F3FC;border-color:#7CB9D8}.station.closed{background:#F6F0EA;border-color:#D7A96C}
    .panel{background:white;border:1px solid #DFE8EF;border-radius:14px;padding:14px;margin-bottom:10px}
    .achievement{display:inline-block;background:#FFF1BE;color:#805C09;border-radius:99px;padding:5px 9px;margin:2px;font-size:.72rem;font-weight:800}
    .status-ok{background:#E8F8EF;border-left:5px solid #1B9158;padding:9px 12px;border-radius:9px}.status-warn{background:#FFF1E1;border-left:5px solid #D98225;padding:9px 12px;border-radius:9px}

    .kpi-grid{display:grid;gap:10px;margin:10px 0 14px}.kpi-grid.cols-4{grid-template-columns:repeat(4,minmax(0,1fr))}.kpi-grid.cols-5{grid-template-columns:repeat(5,minmax(0,1fr))}.kpi-grid.cols-6{grid-template-columns:repeat(6,minmax(0,1fr))}
    .kpi-card{background:#fff;border:1px solid #dce7ee;border-radius:13px;padding:12px 14px;box-shadow:0 5px 14px #133f5f0d}.kpi-card small{display:block;color:#6f8392;font-size:.7rem}.kpi-card b{display:block;color:#123f63;font-size:1.4rem;margin-top:3px}.kpi-card.ok{background:#eaf9ef}.kpi-card.info{background:#edf6ff}.kpi-card.warn{background:#fff0f0}.kpi-card.gold{background:#fff7dc}
    .dl-progress{margin:10px 0}.dl-progress-head{display:flex;justify-content:space-between;font-size:.73rem;color:#dcecff;margin-bottom:5px}.dl-progress-track{height:9px;background:#173d5b;border-radius:99px;overflow:hidden}.dl-progress-track i{display:block;height:100%;background:linear-gradient(90deg,#39a4ff,#73c9ff);border-radius:99px}
    #MainMenu{visibility:hidden}footer{visibility:hidden}
    [data-testid="stSidebarNav"]{display:none!important}
    header[data-testid="stHeader"]{background:transparent}
    @media(max-width:900px){.facility-grid{grid-template-columns:1fr}.dl-top{align-items:flex-start;flex-direction:column}.kpi-grid.cols-4,.kpi-grid.cols-5,.kpi-grid.cols-6{grid-template-columns:repeat(2,minmax(0,1fr))}}
    </style>
    """,unsafe_allow_html=True)

def init_state():
    defaults={
        "scenario":"banco","result":None,"frame":0,"actions":[],"score_history":[],
        "xp":0,"coins":0,"level":1,"completed":set(),"saved":{},"profile_name":"Carlos",
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v

def update_progress(result):
    key=result["scenario"]
    if key not in st.session_state.completed and result["passes"]["budget"] and result["passes"]["sla"]:
        st.session_state.completed.add(key);st.session_state.xp+=100;st.session_state.coins+=100
    else:
        st.session_state.xp+=5;st.session_state.coins+=2
    st.session_state.level=1+st.session_state.xp//500

def sidebar():
    with st.sidebar:
        st.markdown("## ◈ DECISION LAB 2.0")
        st.caption("Teoría de Colas en la Práctica")
        section=st.radio("Navegación",["Inicio","Modelos","Simulación","Challenge","Comparador","Análisis Económico","Red Multietapa","Reportes"],label_visibility="collapsed")
        st.divider()
        st.markdown(f"**{st.session_state.profile_name}** · Nivel {st.session_state.level}")
        progress_html(min(1,(st.session_state.xp%500)/500),f"{st.session_state.xp} XP · ★ {st.session_state.coins}")
        st.caption(f"Desafíos dominados: {len(st.session_state.completed)}/5")
        return section

def topbar():
    st.markdown(f"""<div class="dl-top"><div class="dl-brand">◈ DECISION LAB 2.0<small>Simulación, analítica y gamificación de sistemas de espera</small></div>
    <div><b>{st.session_state.profile_name}</b> · Nivel {st.session_state.level} &nbsp; <b>★ {st.session_state.coins}</b></div></div>""",unsafe_allow_html=True)

def scenario_gallery():
    cols=st.columns(5)
    for col,(key,cfg) in zip(cols,SCENARIOS.items()):
        with col:
            path=SCENE_DIR/f"{key}.svg"
            if path.exists():st.image(str(path),use_container_width=True)
            if st.button(f"{cfg['sector']}\n\n{cfg['name']}",key=f"scene_{key}",use_container_width=True,type="primary" if st.session_state.scenario==key else "secondary"):
                st.session_state.scenario=key;st.session_state.result=None;st.session_state.frame=0;st.rerun()

def facility_html(frame):
    queue=list(frame.get("queue_ids",[]))
    servers=list(frame.get("servers",[]))
    active=int(frame.get("active",0))
    qhtml="".join(f'<span class="client">{x}</span>' for x in queue[:18]) or "<span style='color:#8194A4;font-size:.75rem'>Sin clientes esperando</span>"
    sht=[]
    for i,cid in enumerate(servers):
        if i>=active and cid is None:continue
        cls="busy" if cid is not None else ("closed" if i>=active else "")
        body=f'<span class="client serving">{cid}</span>' if cid is not None else ("Cierre pendiente" if i>=active else "Libre")
        sht.append(f'<div class="station {cls}"><b>Puesto {i+1}</b>{body}</div>')
    return f"""<div class="facility"><div class="facility-grid"><div class="zone"><div class="zone-title">SALA DE ESPERA · {frame.get('queue',0)}</div><div class="queue-people">{qhtml}</div></div>
    <div class="zone"><div class="zone-title">PUESTOS OPERATIVOS · {frame.get('busy',0)} ocupados / {active} activos</div><div class="servers">{''.join(sht)}</div></div></div></div>"""

def run_challenge_ui():
    cfg=SCENARIOS[st.session_state.scenario]
    scenario_gallery()
    st.markdown(f"""<div class="sim-head"><div><h2>Simulación: {cfg['name']} ({cfg['model']})</h2><p>{cfg['sector']} · horizonte de 8 horas · decisiones dinámicas</p></div></div>""",unsafe_allow_html=True)
    with st.expander("Parámetros del escenario",expanded=st.session_state.result is None):
        c1,c2,c3,c4=st.columns(4)
        arrival=c1.number_input("Interarribo promedio (min)",.1,240.0,float(cfg["arrival_min"]),.1)
        service=c2.number_input("Servicio promedio (min)",.1,240.0,float(cfg["service_min"]),.1)
        uniform=c3.number_input("Servidores base",1,int(cfg["max_servers"]),min(4,int(cfg["max_servers"])),1)
        capacity=c4.number_input("Capacidad total",1,1000,int(cfg["capacity"]),1)
        c5,c6,c7,c8=st.columns(4)
        staff_cost=c5.number_input("Costo servidor / h",0.0,10000.0,float(cfg["staff_hour"]),1.0)
        wait_cost=c6.number_input("Costo espera / cliente-h",0.0,10000.0,float(cfg["wait_hour"]),1.0)
        sla_min=c7.number_input("SLA: espera ≤ min",.1,240.0,float(cfg["sla_min"]),.5)
        sla_target=c8.number_input("Meta SLA",0.0,1.0,float(cfg["sla_target"]),.01)
        with st.expander("Opciones avanzadas"):
            a,b,c,d=st.columns(4)
            patience=a.number_input("Paciencia media (0 = sin abandono)",0.0,240.0,0.0,1.0)
            priority=b.number_input("Proporción prioritaria",0.0,1.0,0.0,.05)
            dist=c.selectbox("Distribución servicio",["exponential","deterministic","gamma","lognormal"])
            cv=d.number_input("CV servicio",.05,4.0,1.0,.05)
        reps=st.slider("Réplicas estadísticas",1,50,10)
        staffing=[int(uniform)]*8
        if st.button("▶ Evaluar y simular jornada",type="primary",use_container_width=True):
            payload={"scenario":st.session_state.scenario,"staffing":staffing,"replications":reps,"seed":2026,
                     "arrival_min":arrival,"service_min":service,"capacity":capacity,"staff_hour":staff_cost,"wait_hour":wait_cost,
                     "sla_min":sla_min,"sla_target":sla_target,"patience_min":patience,"priority_share":priority,
                     "service_distribution":dist,"service_cv":cv,"actions":st.session_state.actions}
            st.session_state.result=evaluate_game(payload);st.session_state.frame=0
            st.session_state.score_history.append({"scenario":st.session_state.scenario,"score":st.session_state.result["score"],"metrics":st.session_state.result["metrics"]})
            update_progress(st.session_state.result)
    result=st.session_state.result
    if not result:
        st.info("Configura el escenario y ejecuta la primera simulación.")
        return
    frames=result["events"];idx=min(st.session_state.frame,len(frames)-1);frame=frames[idx]
    metric_cards([("Tiempo simulado",f"{frame['t']:.1f} min","info"),("Atendidos",frame["completed"],"ok"),("En cola",frame["queue"],"info"),("Rechazados",frame["blocked"],"warn")],4)
    st.markdown(facility_html(frame),unsafe_allow_html=True)
    ctrl1,ctrl2,ctrl3,ctrl4=st.columns([1,1,1,5])
    if ctrl1.button("◀",use_container_width=True):st.session_state.frame=max(0,idx-1);st.rerun()
    if ctrl2.button("▶",use_container_width=True):st.session_state.frame=min(len(frames)-1,idx+1);st.rerun()
    if ctrl3.button("≫ +10",use_container_width=True):st.session_state.frame=min(len(frames)-1,idx+10);st.rerun()
    chosen=ctrl4.slider("Línea de tiempo",0,len(frames)-1,idx,key="timeline")
    if chosen!=idx:st.session_state.frame=chosen;st.rerun()
    st.caption(f"Evento {idx}/{len(frames)-1} · {frame['kind']} · llegadas {frame['arrivals']} · abandonos {frame.get('abandoned',0)}")
    with st.expander("Tomar decisión durante la jornada"):
        new_servers=st.number_input("Servidores desde el siguiente minuto",1,int(result["config"]["max_servers"]),int(frame["active"]),1)
        if st.button("Aplicar intervención"):
            minute=max(1,min(int(result["config"]["duration"])-1,int(frame["t"])+1))
            actions=[a for a in st.session_state.actions if a["minute"]<minute]
            actions.append({"minute":minute,"servers":int(new_servers)})
            st.session_state.actions=sorted(actions,key=lambda x:x["minute"])
            payload=dict(result.get("config",{}));payload.update(result.get("options",{}))
            payload.update({"scenario":result["scenario"],"staffing":result["staffing"],"replications":result["replications"],"seed":2026,"actions":st.session_state.actions})
            st.session_state.result=evaluate_game(payload);st.rerun()
    m=result["metrics"]
    st.markdown("### Resultados proyectados al cierre")
    metric_cards([("Score",f"{result['score']}/100","gold"),("SLA",f"{m['sla']*100:.1f}%","ok"),("Espera",f"{m['avg_wait']:.1f} min","info"),("Utilización",f"{m['utilization']*100:.1f}%","info"),("Costo total",f"S/ {m['total_cost']:.2f}","warn"),("Abandonos",f"{m['abandoned']:.1f}","warn")],6)
    status="status-ok" if result["passes"]["budget"] and result["passes"]["sla"] else "status-warn"
    st.markdown(f'<div class="{status}"><b>{"Misión cumplida" if status=="status-ok" else "Estrategia por mejorar"}</b> · '+" · ".join(result["achievements"])+"</div>",unsafe_allow_html=True)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=[x["t"] for x in result["series"]],y=[x["queue"] for x in result["series"]],mode="lines",name="Cola",line_shape="hv"))
    fig.add_trace(go.Scatter(x=[x["t"] for x in result["series"]],y=[x["busy"] for x in result["series"]],mode="lines",name="En servicio",line_shape="hv"))
    fig.update_layout(template="plotly_white",height=320,margin=dict(t=30,l=40,r=20,b=40),xaxis_title="Tiempo (min)",yaxis_title="Clientes")
    st.plotly_chart(fig,use_container_width=True)
    st.download_button("Descargar partida JSON",json.dumps(result,ensure_ascii=False,indent=2),file_name=f"decision-lab-{result['scenario']}.json",mime="application/json")

def model_lab():
    st.header("Modelos matemáticos")
    model=st.selectbox("Modelo",MODELS)
    a,b,c=st.columns(3);arrival=a.number_input("Interarribo (min)",.1,240.0,8.0,.1);service=b.number_input("Servicio (min)",.1,240.0,6.0,.1);servers=c.number_input("Servidores",1,25,2,1)
    try:
        if model in ("M/M/1","M/M/s"):
            r=mms_from_minutes(arrival,service,1 if model=="M/M/1" else int(servers))
        elif model in ("M/M/s/K","M/M/1/c","M/M/s/c"):
            cap=st.number_input("Capacidad total K",int(servers),150,max(int(servers)+5,8),1)
            r=mmsk_from_minutes(arrival,service,1 if model=="M/M/1/c" else int(servers),int(cap))
        elif model=="Erlang B":
            lam,mu=60/arrival,60/service;aoff=lam/mu;bprob=erlang_b(aoff,int(servers));r={"estable":True,"rho":aoff/int(servers),"P_bloqueo":bprob,"P_espera":0,"Lq":0,"Wq":0,"W":service/60,"L":aoff*(1-bprob)}
        elif model=="M/G/1":
            cv=st.number_input("CV servicio",0.0,4.0,1.0,.1);r=mg1_from_minutes(arrival,service,cv)
        else:
            n=st.slider("Clientes",5,100,20);df=pd.DataFrame(dd1_sequence(arrival,service,n));st.dataframe(df,use_container_width=True);st.line_chart(df.set_index("Cliente")["Espera (min)"]);return
        metric_cards([("Estado","Estable" if r.get("estable") else "Inestable","ok" if r.get("estable") else "warn"),("ρ",f"{r.get('rho',0):.3f}","info"),("Lq",f"{r.get('Lq',0):.2f}","info"),("Wq",f"{r.get('Wq',0)*60:.2f} min" if math.isfinite(r.get("Wq",0)) else "∞","info"),("Bloqueo",f"{r.get('P_bloqueo',0)*100:.1f}%","warn")],5)
        st.json(r)
    except ValueError as exc:st.error(str(exc))

def comparator():
    st.header("Comparador de escenarios")
    c1,c2=st.columns(2)
    configs=[]
    for i,col in enumerate((c1,c2),1):
        with col:
            st.subheader(f"Escenario {i}")
            arr=st.number_input("Interarribo",.1,240.0,4.0,key=f"ca{i}");srv=st.number_input("Servicio",.1,240.0,6.0,key=f"cs{i}");s=st.number_input("Servidores",1,20,2+i-1,key=f"cn{i}")
            r=mms_from_minutes(arr,srv,int(s));configs.append((s,r))
    rows=[]
    for i,(s,r) in enumerate(configs,1):rows.append({"Escenario":i,"Servidores":s,"Utilización %":r["rho"]*100,"Wq min":r["Wq"]*60 if r["estable"] else None,"P espera %":r["P_espera"]*100})
    df=pd.DataFrame(rows);st.dataframe(df,use_container_width=True);st.bar_chart(df.set_index("Escenario")["Wq min"])

def economics():
    st.header("Análisis económico")
    c1,c2,c3=st.columns(3);arrival=c1.number_input("Interarribo",.1,240.0,4.0,key="ea");service=c2.number_input("Servicio",.1,240.0,6.0,key="es");maxs=c3.slider("Servidores a evaluar",1,15,8)
    c4,c5,c6=st.columns(3);cs=c4.number_input("Costo servidor/h",0.0,10000.0,20.0);cw=c5.number_input("Costo espera cliente-h",0.0,10000.0,12.0);goal=c6.number_input("Meta Wq min",.1,240.0,5.0)
    rows,rec=recommend_mms_capacity(arrival,service,maxs,cs,cw,goal)
    df=pd.DataFrame(rows);st.dataframe(df,use_container_width=True);st.success(f"Alternativa recomendada: {rec['servers']} servidores · Wq {rec['Wq_min']:.2f} min · costo S/ {rec['cost_total']:.2f}/h")
    st.line_chart(df.set_index("servers")[["cost_staff","cost_wait","cost_total"]])

def network():
    st.header("Red de colas multietapa")
    c1,c2=st.columns(2);arrival=c1.number_input("Interarribo (min)",.1,240.0,4.0,key="na");horizon=c2.number_input("Horizonte (min)",30,1440,480)
    count=st.slider("Etapas",2,4,3);stages=[]
    defaults=[("Recepción",5,2),("Atención",8,3),("Pago",4,2),("Entrega",6,2)]
    for i in range(count):
        a,b,c=st.columns([1.2,1,1]);name=a.text_input("Nombre",defaults[i][0],key=f"nn{i}");sm=b.number_input("Servicio min",.1,240.0,float(defaults[i][1]),key=f"ns{i}");sv=c.number_input("Servidores",1,20,int(defaults[i][2]),key=f"nv{i}");stages.append({"name":name,"service_min":sm,"servers":sv})
    if st.button("Simular red",type="primary"):
        r=simulate_network({"arrival_min":arrival,"horizon":horizon,"seed":2026,"stages":stages})
        st.session_state.network_result=r
    if "network_result" in st.session_state:
        r=st.session_state.network_result;metric_cards([("Llegadas",r["arrivals"],"info"),("Completados",r["completed"],"ok"),("Throughput",f"{r['throughput_rate']:.2f}/h","info"),("Tiempo sistema",f"{r['avg_system']:.1f} min","gold")],4)
        df=pd.DataFrame(r["stages"]);st.dataframe(df,use_container_width=True)
        fig=go.Figure()
        for i,stage in enumerate(r["stages"]):fig.add_trace(go.Scatter(x=[f["t"] for f in r["frames"]],y=[f["queues"][i] for f in r["frames"]],mode="lines",name=stage["name"],line_shape="hv"))
        st.plotly_chart(fig,use_container_width=True)

def reports():
    st.header("Reportes y progreso")
    metric_cards([("Nivel",st.session_state.level,"gold"),("XP",st.session_state.xp,"info"),("Monedas",st.session_state.coins,"gold")],3)
    if st.session_state.score_history:
        df=pd.DataFrame([{"Escenario":x["scenario"],"Score":x["score"],"Costo":x["metrics"]["total_cost"],"SLA":x["metrics"]["sla"]} for x in st.session_state.score_history])
        st.dataframe(df,use_container_width=True)
        st.download_button("Descargar historial CSV",df.to_csv(index=False).encode(),file_name="decision-lab-historial.csv",mime="text/csv")
    else:st.info("Todavía no hay partidas en esta sesión.")
    st.caption("En Streamlit Community Cloud el estado de sesión no es una base de datos persistente. La persistencia multiusuario completa permanece en la versión Django/PostgreSQL.")

def home():
    st.markdown("## Decision Lab 2.0")
    st.write("Plataforma de teoría de colas que integra modelos analíticos, simulación de eventos discretos, decisiones gerenciales y gamificación.")
    scenario_gallery()
    metric_cards([("Modelos matemáticos","8","info"),("Escenarios gerenciales","5","ok"),("Etapas en red","2–4","gold"),("Distribuciones servicio","4","info")],4)
    st.info("El tablero operativo se muestra directamente en Inicio para que puedas evaluar la simulación sin navegar a otra sección.")
    run_challenge_ui()

css();init_state();topbar();section=sidebar()
if section=="Inicio":home()
elif section=="Modelos":model_lab()
elif section in ("Simulación","Challenge"):run_challenge_ui()
elif section=="Comparador":comparator()
elif section=="Análisis Económico":economics()
elif section=="Red Multietapa":network()
else:reports()
