"""Finite-horizon tandem queue network simulator (2–10 stages)."""
from collections import deque
from heapq import heappop, heappush
from math import isfinite, ceil
from random import Random

def _num(value,name,lo,hi):
    try:n=float(value)
    except (TypeError,ValueError,OverflowError) as exc:raise ValueError(f"{name} inválido") from exc
    if not isfinite(n) or not lo<=n<=hi:raise ValueError(f"{name} debe estar entre {lo} y {hi}")
    return n

def _integer(value,name,lo,hi):
    n=_num(value,name,lo,hi)
    if int(n)!=n:raise ValueError(f"{name} debe ser entero")
    return int(n)

def simulate_network(payload):
    if not isinstance(payload,dict):raise ValueError("Se requiere configuración")
    arrival_min=_num(payload.get("arrival_min",4),"arrival_min",.1,240)
    horizon=_num(payload.get("horizon",480),"horizon",30,1440)
    seed=_integer(payload.get("seed",2026),"seed",1,999999999)
    raw=payload.get("stages") or [{"name":"Recepción","service_min":5,"servers":2},{"name":"Atención","service_min":8,"servers":3}]
    if not isinstance(raw,list) or not 2<=len(raw)<=10:raise ValueError("La red requiere entre 2 y 10 etapas")
    stages=[]
    for i,item in enumerate(raw):
        if not isinstance(item,dict):raise ValueError("Etapa inválida")
        stages.append({"name":str(item.get("name") or f"Etapa {i+1}")[:50],
            "service_min":_num(item.get("service_min"),f"service_min etapa {i+1}",.1,240),
            "servers":_integer(item.get("servers"),f"servers etapa {i+1}",1,20)})
    arng=Random(seed);srng=[Random(seed+10000*(i+1)) for i in range(len(stages))]
    arrivals=[];t=arng.expovariate(1/arrival_min)
    while t<horizon:
        arrivals.append(t);t+=arng.expovariate(1/arrival_min)
    service={i:{cid:srng[i].expovariate(1/stages[i]["service_min"]) for cid in range(1,len(arrivals)+1)} for i in range(len(stages))}
    queues=[deque() for _ in stages];servers=[[None]*stage["servers"] for stage in stages]
    events=[];order=0
    def schedule(time,kind,cid,stage=-1,slot=-1):
        nonlocal order;order+=1;heappush(events,(time,0 if kind=="departure" else 1,order,kind,cid,stage,slot))
    for cid,time in enumerate(arrivals,1):schedule(time,"external",cid)
    first_arrival={cid:t for cid,t in enumerate(arrivals,1)}
    wait_total=[0.0]*len(stages);started=[0]*len(stages);completed_stage=[0]*len(stages)
    area_q=[0.0]*len(stages);area_busy=[0.0]*len(stages);max_q=[0]*len(stages)
    completed=0;system_total=0.0;last=0.0
    arrived_stage=[0]*len(stages)
    # Acotar el número de fotogramas conservando todos los estados en el motor.
    frame_stride=max(1,ceil(max(1,len(arrivals)*(len(stages)+1))/2800))
    frame_counter=0
    frames=[]
    def advance_areas(time):
        nonlocal last
        dt=time-last
        for i in range(len(stages)):
            area_q[i]+=len(queues[i])*dt
            area_busy[i]+=sum(x is not None for x in servers[i])*dt
        last=time
    def snapshot(time,kind="state",cid=0,stage_i=-1):
        occupancy=[sum(v is not None for v in ss) for ss in servers]
        return {"t":round(time,3),"kind":kind,"client":cid,"stage":stage_i,
            "queues":[len(q) for q in queues],"busy":occupancy,
            "completed":completed,"arrivals":arrived_stage[0],
            "arrived_stage":list(arrived_stage),"completed_stage":list(completed_stage),
            "queue_ids":[[x[0] for x in q][:10] for q in queues],
            "service_ids":[list(ss) for ss in servers],
            "avg_wait_stage":[round(wait_total[i]/max(1,started[i]),4) for i in range(len(stages))],
            "utilization_stage":[round(area_busy[i]/max(time*stages[i]["servers"],1e-9),5)
                                 for i in range(len(stages))]}
    frames.append(snapshot(0,"start"))
    def try_start(stage_i,time):
        while queues[stage_i]:
            try:slot=servers[stage_i].index(None)
            except ValueError:break
            cid,arrived=queues[stage_i].popleft()
            wait_total[stage_i]+=time-arrived;started[stage_i]+=1;servers[stage_i][slot]=cid
            schedule(time+service[stage_i][cid],"departure",cid,stage_i,slot)
    while events:
        time,_,_,kind,cid,stage_i,slot=heappop(events)
        if time>horizon:break
        advance_areas(time)
        if kind=="external":
            arrived_stage[0]+=1
            queues[0].append((cid,time));try_start(0,time)
        else:
            servers[stage_i][slot]=None;completed_stage[stage_i]+=1;try_start(stage_i,time)
            if stage_i+1<len(stages):
                arrived_stage[stage_i+1]+=1
                queues[stage_i+1].append((cid,time));try_start(stage_i+1,time)
            else:
                completed+=1;system_total+=time-first_arrival[cid]
        for i in range(len(stages)):max_q[i]=max(max_q[i],len(queues[i]))
        frame_counter+=1
        if frame_counter % frame_stride==0 and len(frames)<2999:
            frames.append(snapshot(time,kind,cid,stage_i))
    advance_areas(horizon)
    stage_metrics=[]
    for i,stage in enumerate(stages):
        admitted_here=len(arrivals) if i==0 else completed_stage[i-1]
        active_here=sum(v is not None for v in servers[i])
        waiting_here=len(queues[i])
        remaining=admitted_here-completed_stage[i]
        if remaining!=active_here+waiting_here:
            raise RuntimeError(f"La etapa {i+1} no conserva las entidades")
        stage_metrics.append({**stage,
            "arrived":admitted_here,"completed":completed_stage[i],
            "in_stage_at_close":remaining,"waiting_at_close":waiting_here,
            "in_service_at_close":active_here,
            "avg_wait":wait_total[i]/max(1,started[i]),
            "avg_queue":area_q[i]/horizon,
            "utilization":area_busy[i]/(horizon*stage["servers"]),
            "max_queue":max_q[i],"started":started[i]})
    in_system=sum(m["in_stage_at_close"] for m in stage_metrics)
    if len(arrivals)!=completed+in_system:
        raise RuntimeError("La red no conserva la cantidad global de entidades")
    final=snapshot(float(horizon),"end")
    frames.append(final)
    return {"arrival_min":arrival_min,"horizon":horizon,"arrivals":len(arrivals),"completed":completed,
        "throughput_rate":completed/(horizon/60),"avg_system":system_total/max(1,completed),
        "in_system_at_close":in_system,"stages":stage_metrics,"frames":frames,"seed":seed,
        "engine":"network_engine","model":"Tándem M/M/c","mode":"parametric",
         "frame_sample_stride":frame_stride}
