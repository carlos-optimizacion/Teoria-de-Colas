"""Decision Lab Challenge: motor determinista de partidas gerenciales.
No sustituye el cálculo estacionario de queue_core: simula trayectorias de horizonte finito.
"""
from collections import deque
from heapq import heappop, heappush
from random import Random
from math import isfinite
from statistics import mean, stdev
from math import sqrt

SCENARIOS = {
 "banco": {"name":"Banco en hora punta","sector":"Banca","arrival_min":4,"service_min":6,"duration":480,"max_servers":8,"staff_hour":23,"wait_hour":13,"lost_cost":60,"sla_min":10,"sla_target":0.90,"budget":1100,"capacity":24,"incident":"demanda","difficulty":1},
 "hospital": {"name":"Urgencias ambulatorias","sector":"Salud","arrival_min":3,"service_min":9,"duration":480,"max_servers":10,"staff_hour":42,"wait_hour":34,"lost_cost":180,"sla_min":15,"sla_target":0.90,"budget":2500,"capacity":40,"incident":"ausencia","difficulty":3},
 "supermercado": {"name":"Cajas de supermercado","sector":"Retail","arrival_min":2,"service_min":7,"duration":480,"max_servers":12,"staff_hour":19,"wait_hour":10,"lost_cost":45,"sla_min":8,"sla_target":0.85,"budget":1700,"capacity":35,"incident":"demanda","difficulty":2},
 "fabrica": {"name":"Inspección industrial","sector":"Manufactura","arrival_min":5,"service_min":12,"duration":480,"max_servers":8,"staff_hour":30,"wait_hour":20,"lost_cost":90,"sla_min":12,"sla_target":0.90,"budget":1600,"capacity":30,"incident":"averia","difficulty":4},
 "logistica": {"name":"Andenes de despacho","sector":"Logística","arrival_min":3,"service_min":10,"duration":480,"max_servers":10,"staff_hour":28,"wait_hour":22,"lost_cost":100,"sla_min":15,"sla_target":0.90,"budget":1800,"capacity":32,"incident":"demanda","difficulty":3},
}
def _validated_int(value,name,lo,hi):
    try:
        numeric=float(value)
    except (ValueError,TypeError,OverflowError):
        raise ValueError(f"{name} debe ser entero")
    if isinstance(value,bool) or not isfinite(numeric) or numeric!=int(numeric): raise ValueError(f"{name} debe ser entero")
    value=int(value)
    if not lo<=value<=hi: raise ValueError(f"{name} fuera del intervalo [{lo},{hi}]")
    return value

def evaluate_game(payload):
    """Una jornada: acciones programadas en bloques de 60 min; mismas realizaciones
    aleatorias para comparar dotaciones; se contabiliza coste de capacidad programada.
    """
    key=payload.get("scenario","banco")
    if key not in SCENARIOS: raise ValueError("Escenario no identificado")
    cfg=SCENARIOS[key]
    seed=_validated_int(payload.get("seed",2026),"seed",1,999999999)
    reps=_validated_int(payload.get("replications",10),"replications",1,50)
    blocks=cfg["duration"]//60
    raw=payload.get("staffing",[3]*blocks)
    if not isinstance(raw,list) or len(raw)!=blocks: raise ValueError(f"staffing requiere {blocks} bloques horarios")
    staff=[_validated_int(v,"servidores",1,cfg["max_servers"]) for v in raw]
    trials=[_run(cfg,staff,seed+i*1709,key) for i in range(reps)]
    keys=["arrivals","admitted","blocked","completed","unserved_at_close","avg_wait","avg_system","sla","p_block","utilization","avg_queue","staff_cost","waiting_cost","lost_cost","total_cost","max_queue"]
    metrics={k:round(mean(t[k] for t in trials),4) for k in keys}
    confidence={}
    for measure in ("sla","avg_wait","total_cost","p_block"):
        values=[r[measure] for r in trials]
        se=stdev(values)/sqrt(reps) if reps>1 else None
        confidence[measure]={"mean":metrics[measure], "low":round(mean(values)-1.96*se,4) if se is not None else None,"high":round(mean(values)+1.96*se,4) if se is not None else None, "method":"aproximación normal 95%; exploratoria"}
    within_budget=metrics["staff_cost"]<=cfg["budget"]
    meets_sla=metrics["sla"]>=cfg["sla_target"]
    # Los puntos son criterios publicados, nunca se computan con un 'óptimo' desconocido.
    cost_eff=max(0,1-min(1,metrics["total_cost"]/(cfg["budget"]+cfg["lost_cost"]*max(1,metrics["arrivals"])*0.3)))
    loss_eff=1-metrics["blocked"]/max(1,metrics["arrivals"])
    resilience=max(0,1-metrics["unserved_at_close"]/max(1,metrics["admitted"]))
    score=round(35*cost_eff+30*min(1,metrics["sla"]/cfg["sla_target"])+20*loss_eff+15*resilience,1)
    if not within_budget or not meets_sla: score=min(score,69.9)
    return {"scenario":key,"title":cfg["name"],"config":cfg,"staffing":staff,"replications":reps,
       "metrics":metrics,"confidence_95":confidence,"score":score,"passes":{"budget":within_budget,"sla":meets_sla},
       "events":trials[0]["events"],"series":trials[0]["series"],
       "method":"Horizonte finito; clientes pendientes al cierre reportados por separado; promedios sobre replicas independientes."}

def _run(c,staff,seed,key):
    arrival_rng=Random(seed)
    service_rng=Random(seed+100003)
    horizon=c["duration"]
    events=[]; order=0; arrivals_at=[]; arrival_time={}; service_time={}
    t=arrival_rng.expovariate(1/c["arrival_min"])
    while t<horizon:
        # Afluencia extraordinaria predefinida, idéntica entre alternativas.
        arrivals_at.append(t)
        intensity=1.65 if (c["incident"]=="demanda" and horizon*.45<=t<horizon*.7) else 1
        t+=arrival_rng.expovariate(intensity/c["arrival_min"])
    for cid,t in enumerate(arrivals_at,1):
        arrival_time[cid]=t
        service_time[cid]=service_rng.expovariate(1/c["service_min"])
        heappush(events,(t,1,cid,"arrival",None))
    servers=[None]*c["max_servers"]; queue=deque()
    last=0.; area_q=0.; busy_area=0.; total_wait=0.; total_system=0.; admitted=blocked=completed=started=on_time=0
    wait_cost=0.; max_queue=0; timeline=[]; series=[{"t":0,"queue":0,"busy":0}]
    staff_cost=sum(n*c["staff_hour"] for n in staff)
    # Evaluar también los límites horarios aun si no hay llegadas.
    for boundary in range(1,len(staff)):
        heappush(events,(boundary*60,2,0,"staff_change",None))
    for boundary in (horizon*.45,horizon*.60,horizon*.70):
        heappush(events,(boundary,2,0,"staff_change",None))
    for t,_,cid,kind,server_idx in iter(lambda:heappop(events) if events else None,None):
        if t>horizon: break
        dt=t-last
        area_q+=len(queue)*dt
        busy_area+=sum(x is not None for x in servers)*dt
        wait_cost+=len(queue)*dt*c["wait_hour"]/60
        last=t
        block=min(int(t//60),len(staff)-1)
        active=staff[block]
        # Ausencia/avería reduce temporalmente la capacidad operativa real.
        if c["incident"] in ("ausencia","averia") and horizon*.45<=t<horizon*.60:
            active=max(1,active-1)
        if kind=="arrival":
            if len(queue)+sum(x is not None for x in servers)>=c["capacity"]:
                blocked+=1
            else:
                admitted+=1
                queue.append((cid,t))
        elif kind=="departure":
            completed+=1
            total_system+=t-arrival_time[cid]
            servers[server_idx]=None
        # Sólo posiciones habilitadas admiten NUEVOS trabajos; no se expulsa el servicio en curso.
        for idx in range(active):
            if servers[idx] is None and queue:
                next_id,at=queue.popleft()
                started+=1; w=t-at; total_wait+=w
                if w<=c["sla_min"]:on_time+=1
                servers[idx]=next_id
                duration=service_time[next_id]
                order+=1
                heappush(events,(t+duration,0,next_id,"departure",idx))
        max_queue=max(max_queue,len(queue))
        if len(timeline)<2000:timeline.append({"t":round(t,2),"kind":kind,"client":cid,"queue":len(queue),"busy":sum(x is not None for x in servers),"active":active})
        if len(series)<2000:series.append({"t":round(t,2),"queue":len(queue),"busy":sum(x is not None for x in servers)})
    # Correctamente se mantienen las pendientes a cierre sin simular salidas fuera de ventana.
    remaining=horizon-last
    area_q+=len(queue)*remaining
    busy_area+=sum(x is not None for x in servers)*remaining
    wait_cost+=len(queue)*remaining*c["wait_hour"]/60
    outstanding=admitted-completed
    # SLA conservador: todos los admitidos, incluidos pendientes, componen el denominador.
    sla=on_time/max(1,admitted)
    loss=blocked*c["lost_cost"]
    return {"arrivals":len(arrivals_at),"admitted":admitted,"blocked":blocked,"completed":completed,
     "unserved_at_close":outstanding,"avg_wait":total_wait/max(1,started),
     "avg_system":total_system/max(1,completed),"sla":sla,"p_block":blocked/max(1,len(arrivals_at)),
     "utilization":busy_area/max(1,sum(staff)*60),"avg_queue":area_q/horizon,
     "staff_cost":staff_cost,"waiting_cost":wait_cost,"lost_cost":loss,"total_cost":staff_cost+wait_cost+loss,
     "max_queue":max_queue,"events":timeline,"series":series}
