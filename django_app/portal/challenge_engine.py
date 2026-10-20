"""Simulation-backed management challenges for Decision Lab.

Finite-horizon FCFS queueing, common random numbers by customer ID, hourly
staffing, time-specific player interventions, capacity limits and scenario shocks.
All economic figures are illustrative parameters supplied by the exercise.
"""
from heapq import heappop, heappush
from math import isfinite, sqrt
from random import Random
from statistics import mean, stdev

SCENARIOS = {
    "banco": dict(name="Banco en hora punta", sector="Banca", model="M/M/s/K", arrival_min=4, service_min=6, duration=480, max_servers=8, staff_hour=23, wait_hour=13, lost_cost=60, sla_min=10, sla_target=.90, budget=1100, capacity=24, incident="demanda", difficulty=1),
    "hospital": dict(name="Urgencias ambulatorias", sector="Salud", model="M/M/s/K", arrival_min=3, service_min=9, duration=480, max_servers=10, staff_hour=42, wait_hour=34, lost_cost=180, sla_min=15, sla_target=.90, budget=2500, capacity=40, incident="ausencia", difficulty=3),
    "supermercado": dict(name="Cajas de supermercado", sector="Retail", model="M/M/s/K", arrival_min=2, service_min=7, duration=480, max_servers=12, staff_hour=19, wait_hour=10, lost_cost=45, sla_min=8, sla_target=.85, budget=1700, capacity=35, incident="demanda", difficulty=2),
    "fabrica": dict(name="Inspección industrial", sector="Manufactura", model="M/M/s/K", arrival_min=5, service_min=12, duration=480, max_servers=8, staff_hour=30, wait_hour=20, lost_cost=90, sla_min=12, sla_target=.90, budget=1600, capacity=30, incident="averia", difficulty=4),
    "logistica": dict(name="Andenes de despacho", sector="Logística", model="M/M/s/K", arrival_min=3, service_min=10, duration=480, max_servers=10, staff_hour=28, wait_hour=22, lost_cost=100, sla_min=15, sla_target=.90, budget=1800, capacity=32, incident="demanda", difficulty=3),
}

def _integer(value, name, lo, hi):
    try:
        n = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} debe ser un entero válido") from exc
    if isinstance(value, bool) or not isfinite(n) or not n.is_integer() or not lo <= n <= hi:
        raise ValueError(f"{name} debe ser un entero entre {lo} y {hi}")
    return int(n)

def _number(value,name,lo,hi):
    try:
        n=float(value)
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError(f"{name} debe ser numérico") from exc
    if not isfinite(n) or n < lo or n > hi:
        raise ValueError(f"{name} debe estar entre {lo} y {hi}")
    return n

def _actions(raw, config):
    if not isinstance(raw, list) or len(raw) > 24:
        raise ValueError("actions debe ser una lista de máximo 24 intervenciones")
    result = []
    prev = -1
    for action in raw:
        if not isinstance(action, dict):
            raise ValueError("Cada intervención debe ser un objeto")
        minute = _integer(action.get("minute"), "minute", 1, config["duration"] - 1)
        number = _integer(action.get("servers"), "servers", 1, config["max_servers"])
        if minute <= prev:
            raise ValueError("Las intervenciones deben ordenarse por minuto sin duplicados")
        result.append({"minute": minute, "servers": number})
        prev = minute
    return result

def _arrivals(config, seed):
    """A piecewise Poisson arrival process; demand incident = 65% surge."""
    rng = Random(seed)
    end = config["duration"]
    segments = [(0., end*.45, 1.), (end*.45, end*.70, 1.65), (end*.70, end, 1.)] if config["incident"] == "demanda" else [(0., end, 1.)]
    result = []
    for start, stop, multiplier in segments:
        t = start
        while True:
            t += rng.expovariate(multiplier / config["arrival_min"])
            if t >= stop:
                break
            result.append(t)
    return result

def _run(config, staffing, actions, seed, options=None):
    options=options or {}
    patience_min=float(options.get("patience_min",0) or 0)
    priority_share=float(options.get("priority_share",0) or 0)
    horizon = config["duration"]
    arrivals = _arrivals(config, seed)
    service_rng = Random(seed + 100003)
    patience_rng = Random(seed + 200003)
    priority_rng = Random(seed + 300003)
    service_duration = {i: service_rng.expovariate(1 / config["service_min"]) for i in range(1, len(arrivals)+1)}
    arrival_time = {i: t for i, t in enumerate(arrivals, 1)}
    events, order = [], 0
    def schedule(time, priority, kind, cid=0, slot=-1):
        nonlocal order
        order += 1
        heappush(events, (time, priority, order, kind, cid, slot))
    for cid, t in enumerate(arrivals, 1):
        schedule(t, 3, "arrival", cid)
    for hour in range(1, len(staffing)):
        schedule(hour*60, 2, "shift")
    for moment in (horizon*.45, horizon*.60):
        if config["incident"] in ("averia", "ausencia"):
            schedule(moment, 2, "incident")
    for action in actions:
        schedule(action["minute"], 1, "decision", action["servers"])
    servers = [None] * config["max_servers"]
    waiting = []
    waiting_ids = set()
    class_priority = {i: (0 if priority_rng.random() < priority_share else 1) for i in range(1,len(arrivals)+1)}
    override = None
    last = 0.
    area_queue = area_busy = capacity_area = wait_cost = staff_cost = 0.
    admitted = rejected = abandoned = finished = started = compliant = 0
    total_wait = total_system = max_queue = 0.
    frames = [{"t": 0, "kind": "start", "client": None, "queue": 0, "queue_ids": [], "busy": 0, "servers": list(servers), "active": staffing[0], "arrivals": 0, "completed": 0, "blocked": 0, "abandoned": 0}]
    series = [{"t": 0, "queue": 0, "busy": 0}]
    def levels(time):
        planned = override if override is not None else staffing[min(int(time // 60), len(staffing)-1)]
        incident = config["incident"] in ("averia", "ausencia") and horizon*.45 <= time < horizon*.60
        return planned, max(1, planned-1) if incident else planned
    arrivals_processed = 0
    for t, _, _, kind, cid, slot in events_iterator(events):
        if t > horizon:
            break
        dt = t-last
        planned, active = levels(last)
        occupied = sum(x is not None for x in servers)
        area_queue += len(waiting) * dt
        area_busy += occupied * dt
        capacity_area += max(active, occupied) * dt
        wait_cost += len(waiting)*dt*config["wait_hour"]/60.
        staff_cost += planned*dt*config["staff_hour"]/60.
        last = t
        label = kind
        if kind == "decision":
            override = cid
        elif kind == "arrival":
            arrivals_processed += 1
            if len(waiting) + occupied >= config["capacity"]:
                rejected += 1
                label = "blocked"
            else:
                admitted += 1
                waiting.append((class_priority[cid], order, cid, t))
                waiting.sort(key=lambda x:(x[0],x[1]))
                waiting_ids.add(cid)
                if patience_min > 0:
                    patience=patience_rng.expovariate(1/patience_min)
                    schedule(t+patience,1,"abandon",cid)
        elif kind == "departure":
            finished += 1
            total_system += t - arrival_time[cid]
            servers[slot] = None
        elif kind == "abandon":
            if cid in waiting_ids:
                waiting[:] = [item for item in waiting if item[2] != cid]
                waiting_ids.discard(cid)
                abandoned += 1
                label = "abandon"
        _, active = levels(t)
        for s in range(active):
            if servers[s] is not None or not waiting:
                continue
            _, _, next_id, arrived = waiting.pop(0)
            waiting_ids.discard(next_id)
            wait = t-arrived
            started += 1
            total_wait += wait
            compliant += int(wait <= config["sla_min"])
            servers[s] = next_id
            schedule(t + service_duration[next_id], 0, "departure", next_id, s)
        max_queue = max(max_queue, len(waiting))
        current_busy = sum(x is not None for x in servers)
        if len(frames) < 3000:
            frames.append({"t": round(t,3), "kind": label, "client": cid if kind in ("arrival", "departure", "abandon") else None,
                "queue": len(waiting), "queue_ids": [x[2] for x in waiting[:20]],
                "busy": current_busy, "servers": list(servers), "active": active,
                "arrivals": arrivals_processed, "completed": finished, "blocked": rejected, "abandoned": abandoned,
                "priority_ids":[x[2] for x in waiting if x[0]==0][:20] + [x for x in servers if x is not None and class_priority.get(x)==0]})
        if len(series) < 3000:
            series.append({"t": round(t,3), "queue": len(waiting), "busy": current_busy})
    dt = max(0., horizon-last)
    planned, active = levels(last)
    occupied = sum(x is not None for x in servers)
    area_queue += len(waiting)*dt
    area_busy += occupied*dt
    capacity_area += max(active,occupied)*dt
    wait_cost += len(waiting)*dt*config["wait_hour"]/60.
    staff_cost += planned*dt*config["staff_hour"]/60.
    if len(frames) < 3000:
        frames.append({"t": horizon, "kind": "end", "client": None, "queue": len(waiting),
            "queue_ids": [x[2] for x in waiting[:20]], "busy": occupied, "servers": list(servers),
            "active": active, "arrivals": arrivals_processed, "completed": finished, "blocked": rejected, "abandoned": abandoned})
    outstanding = admitted-finished-abandoned
    lost = rejected*config["lost_cost"] + abandoned*config["lost_cost"]*.5
    return {"arrivals": len(arrivals), "admitted": admitted, "blocked": rejected, "abandoned": abandoned,
        "completed": finished, "started": started, "unserved_at_close": outstanding,
        "avg_wait": total_wait/max(started,1), "avg_system": total_system/max(finished,1),
        "sla": compliant/max(admitted,1), "p_block": rejected/max(len(arrivals),1), "p_abandon": abandoned/max(admitted,1),
        "utilization": area_busy/max(capacity_area,1), "avg_queue": area_queue/horizon,
        "staff_cost": staff_cost, "waiting_cost": wait_cost, "lost_cost": lost,
        "total_cost": staff_cost + wait_cost + lost, "max_queue": max_queue,
        "events": frames, "series": series}

def events_iterator(heap):
    while heap:
        yield heappop(heap)

def evaluate_game(payload):
    """Evaluate a single decision strategy; no side effects or server-side persistence."""
    if not isinstance(payload, dict):
        raise ValueError("Se requiere un escenario JSON")
    key = payload.get("scenario", "banco")
    if key not in SCENARIOS:
        raise ValueError("Escenario no identificado")
    cfg = dict(SCENARIOS[key])
    override_specs={
        "arrival_min":(.1,240),"service_min":(.1,240),"staff_hour":(0,10000),
        "wait_hour":(0,10000),"lost_cost":(0,100000),"sla_min":(.1,240),
        "sla_target":(0,1),"budget":(0,10000000),
    }
    for field,(lo,hi) in override_specs.items():
        if field in payload:
            cfg[field]=_number(payload[field],field,lo,hi)
    if "capacity" in payload:
        cfg["capacity"]=_integer(payload["capacity"],"capacity",1,1000)
    seed = _integer(payload.get("seed",2026), "seed", 1, 999999999)
    replications = _integer(payload.get("replications",10), "replications", 1, 50)
    staffing = payload.get("staffing", [3] * (cfg["duration"] // 60))
    if not isinstance(staffing, list) or len(staffing) != cfg["duration"] // 60:
        raise ValueError("Se requiere una dotación por cada hora")
    staffing = [_integer(s, "servidores", 1, cfg["max_servers"]) for s in staffing]
    actions = _actions(payload.get("actions", []), cfg)
    options={"patience_min":_number(payload.get("patience_min",0),"patience_min",0,240),"priority_share":_number(payload.get("priority_share",0),"priority_share",0,1)}
    runs = [_run(cfg, staffing, actions, seed + i*1709, options) for i in range(replications)]
    columns = ("arrivals","admitted","blocked","abandoned","completed","started","unserved_at_close",
        "avg_wait","avg_system","sla","p_block","p_abandon","utilization","avg_queue",
        "staff_cost","waiting_cost","lost_cost","total_cost","max_queue")
    metrics = {name: round(mean(r[name] for r in runs),4) for name in columns}
    confidence = {}
    for name in ("sla", "avg_wait", "total_cost", "p_block", "p_abandon"):
        values = [r[name] for r in runs]
        error = 1.96*stdev(values)/sqrt(replications) if replications > 1 else None
        low = max(0, mean(values)-error) if error is not None else None
        high = min(1,mean(values)+error) if error is not None and name in ("sla","p_block","p_abandon") else (mean(values)+error if error is not None else None)
        confidence[name] = {"mean":metrics[name], "low":round(low,4) if low is not None else None,
            "high":round(high,4) if high is not None else None, "method":"intervalo normal exploratorio 95%"}
    budget = metrics["staff_cost"] <= cfg["budget"]
    service = metrics["sla"] >= cfg["sla_target"]
    baseline = cfg["budget"] + cfg["lost_cost"]*max(1,metrics["arrivals"])*.3
    cost_score = max(0,1-min(1,metrics["total_cost"]/baseline))
    loss_score = 1-(metrics["blocked"]+metrics["abandoned"])/max(1,metrics["arrivals"])
    resilience = 1-metrics["unserved_at_close"]/max(1,metrics["admitted"])
    score = round(35*cost_score+30*min(1,metrics["sla"]/cfg["sla_target"])
        +20*loss_score+15*resilience,1)
    if not budget or not service:
        score = min(score,69.9)
    achievements = []
    if budget: achievements.append("Disciplina presupuestaria")
    if service: achievements.append("Calidad de servicio")
    if metrics["blocked"] == 0: achievements.append("Sin rechazos")
    if metrics["abandoned"] == 0: achievements.append("Sin abandonos")
    if budget and service: achievements.append("Misión cumplida")
    return {"scenario":key, "title":cfg["name"],"config":cfg,
        "staffing":staffing,"actions":actions,"options":options,"replications":replications,"metrics":metrics,
        "confidence_95":confidence,"score":score,"achievements":achievements,
        "passes":{"budget":budget,"sla":service},"events":runs[0]["events"],"series":runs[0]["series"],
        "method":("Prioridad no expropiativa" if options["priority_share"]>0 else "FIFO")+", horizonte finito; SLA sobre admitidos, incluidos pendientes y abandonos; promedios de réplicas independientes, visualización de la primera réplica."}
