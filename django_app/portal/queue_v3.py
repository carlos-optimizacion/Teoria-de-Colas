"""Decision Lab 3.0: motor multimodelo de eventos discretos.

Un solo contrato de eventos para modelos D/D/c, M/M/c, M/M/c/K, Erlang B,
M/G/1, M/G/c, G/G/1 y G/G/c. Las trayectorias provienen siempre de Python;
la interfaz 3D, los gráficos y los reportes son consumidores de estos eventos.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from statistics import mean, stdev
from typing import Any

MODELS = {
    "D/D/1": ("deterministic", "deterministic", 1, False, False),
    "D/D/c": ("deterministic", "deterministic", None, False, False),
    "M/M/1": ("exponential", "exponential", 1, False, False),
    "M/M/c": ("exponential", "exponential", None, False, False),
    "M/M/1/K": ("exponential", "exponential", 1, True, False),
    "M/M/c/K": ("exponential", "exponential", None, True, False),
    "M/M/c/c (Erlang B)": ("exponential", "exponential", None, True, True),
    "M/G/1": ("exponential", "general", 1, False, False),
    "M/G/c": ("exponential", "general", None, False, False),
    "G/G/1": ("general", "general", 1, False, False),
    "G/G/c": ("general", "general", None, False, False),
}

DISTRIBUTIONS = ("deterministic", "exponential", "gamma", "lognormal", "triangular", "empirical")
MAX_EVENTS = 15000
MAX_REPLICATIONS = 300


def _number(x: Any, name: str, lo: float, hi: float) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name}: se requiere un número") from exc
    if not math.isfinite(v) or v < lo or v > hi:
        raise ValueError(f"{name}: debe estar entre {lo} y {hi}")
    return v


def _integer(x: Any, name: str, lo: int, hi: int) -> int:
    v = _number(x, name, lo, hi)
    if not v.is_integer() or isinstance(x, bool):
        raise ValueError(f"{name}: se requiere un entero")
    return int(v)


def _sample(rng: random.Random, name: str, avg: float, cv: float, values: tuple[float, ...]) -> float:
    if name == "deterministic":
        return avg
    if name == "exponential":
        return rng.expovariate(1 / avg)
    if name == "gamma":
        k = 1 / cv**2
        return rng.gammavariate(k, avg / k)
    if name == "lognormal":
        sigma2 = math.log1p(cv**2)
        return rng.lognormvariate(math.log(avg) - sigma2 / 2, math.sqrt(sigma2))
    if name == "triangular":
        # El parámetro "cv" no controla la triangular; se usa min=0.25*media,
        # moda=media y max=2.25*media (media = 1.1667*media nominal).
        # Para preservar la media nominal se utilizan 0.25, 1 y 1.75.
        return rng.triangular(.25 * avg, 1.75 * avg, avg)
    if name == "empirical":
        return rng.choice(values)
    raise ValueError(f"Distribución no admitida: {name}")


@dataclass(frozen=True)
class Specification:
    model: str
    mode: str
    horizon: int
    replications: int
    seed: int
    servers: int
    capacity: int | None
    arrival_mean: float
    service_mean: float
    arrival_dist: str
    service_dist: str
    arrival_cv: float
    service_cv: float
    sla_min: float
    sla_target: float
    server_hour: float
    wait_hour: float
    lost_cost: float
    arrivals_emp: tuple[float, ...]
    services_emp: tuple[float, ...]
    exact_arrivals: tuple[float, ...]


def validate(raw: dict) -> Specification:
    if not isinstance(raw, dict):
        raise ValueError("La configuración debe ser un objeto")
    model = str(raw.get("model", "M/M/c/K"))
    if model not in MODELS:
        raise ValueError("Modelo matemático no reconocido")
    mode = str(raw.get("mode", "parametric"))
    if mode not in {"deterministic", "parametric", "empirical"}:
        raise ValueError("Modalidad desconocida")
    arr_kind, srv_kind, fixed_servers, finite, loss_only = MODELS[model]
    if mode == "deterministic" and (arr_kind != "deterministic" or srv_kind != "deterministic"):
        raise ValueError("Modalidad determinística incompatible con el modelo")
    if mode == "empirical" and (arr_kind == "deterministic" or srv_kind == "deterministic"):
        raise ValueError("El modelo determinístico requiere datos exactos o constantes")
    if mode == "parametric" and arr_kind == "deterministic":
        raise ValueError("El modelo D/D/c utiliza la modalidad determinística")
    horizon = _integer(raw.get("horizon", 480), "Horizonte (min)", 1, 10080)
    replications = _integer(raw.get("replications", 30), "Réplicas", 1, MAX_REPLICATIONS)
    seed = _integer(raw.get("seed", 2026), "Semilla", 1, 999999999)
    servers = _integer(raw.get("servers", 3), "Servidores", 1, 40)
    if fixed_servers is not None and servers != fixed_servers:
        raise ValueError(f"{model} exige exactamente {fixed_servers} servidor")
    capacity = _integer(raw.get("capacity", 24), "Capacidad", servers, 100000) if finite else None
    if loss_only:
        capacity = servers
    arrival_mean = _number(raw.get("arrival_mean", 4), "Interarribo medio", .005, 10080)
    service_mean = _number(raw.get("service_mean", 6), "Servicio medio", .005, 10080)
    ad = str(raw.get("arrival_dist", "deterministic" if arr_kind == "deterministic" else "exponential"))
    sd = str(raw.get("service_dist", "deterministic" if srv_kind == "deterministic" else "exponential"))
    if arr_kind == "deterministic":
        ad = "deterministic"
    elif arr_kind == "exponential" and mode != "empirical":
        ad = "exponential"
    if srv_kind == "deterministic":
        sd = "deterministic"
    elif srv_kind == "exponential" and mode != "empirical":
        sd = "exponential"
    if mode == "empirical":
        ad = sd = "empirical"
    if ad not in DISTRIBUTIONS or sd not in DISTRIBUTIONS:
        raise ValueError("Distribución no reconocida")
    if arr_kind == "exponential" and ad not in {"exponential", "empirical"}:
        raise ValueError("El modelo M requiere interarribos exponenciales")
    if srv_kind == "exponential" and sd not in {"exponential", "empirical"}:
        raise ValueError("El modelo M requiere servicios exponenciales")
    if srv_kind == "general" and sd == "deterministic" and mode == "parametric":
        pass
    acv = _number(raw.get("arrival_cv", 1), "CV de llegadas", .05, 5)
    scv = _number(raw.get("service_cv", 1), "CV de servicio", .05, 5)
    try:
        ae = tuple(float(v) for v in raw.get("arrival_samples", ()))
        se = tuple(float(v) for v in raw.get("service_samples", ()))
        exact = tuple(float(v) for v in raw.get("exact_arrivals", ()))
    except (ValueError, TypeError) as exc:
        raise ValueError("Las muestras deben ser numéricas") from exc
    if any(not math.isfinite(v) or v <= 0 for v in (*ae, *se)):
        raise ValueError("Muestras: todos los intervalos y servicios deben ser positivos")
    if any(not math.isfinite(v) or v < 0 or v >= horizon for v in exact) or tuple(sorted(exact)) != exact:
        raise ValueError("Llegadas programadas: ordenar y ubicar dentro del horizonte")
    if mode == "empirical" and (len(ae) < 2 or len(se) < 2):
        raise ValueError("Se requieren al menos dos interarribos y dos tiempos de atención válidos")
    if len(ae) > 100000 or len(se) > 100000 or len(exact) > MAX_EVENTS // 2:
        raise ValueError("Demasiados datos para una ejecución interactiva")
    return Specification(model, mode, horizon, replications, seed, servers, capacity,
                         arrival_mean, service_mean, ad, sd, acv, scv,
                         _number(raw.get("sla_min", 10), "Umbral SLA", 0, 10080),
                         _number(raw.get("sla_target", .9), "Meta SLA", 0, 1),
                         _number(raw.get("server_hour", 25), "Costo servidor/hora", 0, 100000),
                         _number(raw.get("wait_hour", 10), "Costo espera/hora", 0, 100000),
                         _number(raw.get("lost_cost", 50), "Costo por rechazo", 0, 100000),
                         ae, se, exact)


def _arrivals(spec: Specification, seed: int) -> list[float]:
    if spec.exact_arrivals and spec.mode == "deterministic":
        return list(spec.exact_arrivals)
    rng = random.Random(seed)
    result: list[float] = []
    t = 0.0
    while True:
        gap = _sample(rng, spec.arrival_dist, spec.arrival_mean, spec.arrival_cv, spec.arrivals_emp)
        if not math.isfinite(gap) or gap <= 0:
            raise ValueError("Interarribo no positivo")
        t += gap
        if t >= spec.horizon:
            break
        result.append(t)
        if len(result) > MAX_EVENTS // 2:
            raise ValueError("Demasiadas llegadas: reduzca el horizonte o incremente el intervalo")
    return result


def simulate_one(spec: Specification, seed: int) -> dict:
    import heapq
    arrivals = _arrivals(spec, seed)
    service_rng = random.Random(seed + 100003)
    services = {cid: _sample(service_rng, spec.service_dist, spec.service_mean,
                             spec.service_cv, spec.services_emp) for cid in range(1, len(arrivals) + 1)}
    ev_heap = []
    sequence = 0
    def put(t, priority, kind, cid=0, slot=-1):
        nonlocal sequence
        sequence += 1
        heapq.heappush(ev_heap, (t, priority, sequence, kind, cid, slot))
    for cid, t in enumerate(arrivals, 1):
        put(t, 2, "arrival", cid)
    busy = [None] * spec.servers
    queue: list[int] = []
    waits: list[float] = []
    systems: list[float] = []
    arrival_at = {cid: t for cid, t in enumerate(arrivals, 1)}
    processed = completed = blocked = started = compliant = 0
    wait_area = busy_area = queue_area = 0.
    last = 0.
    max_queue = 0
    frames = [{"t":0., "kind":"start","client":None,"queue":0,"queue_ids":[],"busy":0,
               "servers":list(busy),"active":spec.servers,"arrivals":0,"completed":0,
               "blocked":0,"abandoned":0,"avg_wait_so_far":0., "utilization_so_far":0.}]
    while ev_heap:
        t, _, _, kind, cid, slot = heapq.heappop(ev_heap)
        if t > spec.horizon:
            break
        dt = t - last
        if dt < -1e-9:
            raise RuntimeError("Cronología de eventos no monótona")
        queue_area += len(queue) * dt
        busy_area += sum(b is not None for b in busy) * dt
        wait_area += len(queue) * dt
        last = t
        if kind == "arrival":
            processed += 1
            if spec.capacity is not None and len(queue) + sum(x is not None for x in busy) >= spec.capacity:
                blocked += 1
                kind = "blocked"
            else:
                queue.append(cid)
        elif kind == "departure":
            completed += 1
            systems.append(t - arrival_at[cid])
            busy[slot] = None
        for i, customer in enumerate(busy):
            if customer is not None or not queue:
                continue
            next_id = queue.pop(0)
            delay = t - arrival_at[next_id]
            waits.append(delay)
            compliant += delay <= spec.sla_min
            started += 1
            busy[i] = next_id
            put(t + services[next_id], 0, "departure", next_id, i)
        max_queue = max(max_queue, len(queue))
        current_busy = sum(x is not None for x in busy)
        frames.append({"t":round(t,6),"kind":kind,"client":cid,
                       "queue":len(queue),"queue_ids":list(queue[:42]),"busy":current_busy,
                       "servers":list(busy),"active":spec.servers,
                       "arrivals":processed,"completed":completed,"blocked":blocked,
                       "abandoned":0,"avg_wait_so_far":round(mean(waits),5) if waits else 0.,
                       "utilization_so_far":round(busy_area/(spec.servers*t),6) if t else 0.})
        if len(frames) > MAX_EVENTS:
            raise ValueError("Demasiados eventos para representar. Reduzca duración o intensidad")
    remain = spec.horizon - last
    queue_area += len(queue) * remain
    busy_area += sum(x is not None for x in busy) * remain
    frames.append({"t":float(spec.horizon),"kind":"end","client":None,
                   "queue":len(queue),"queue_ids":list(queue[:42]),
                   "busy":sum(x is not None for x in busy),"servers":list(busy),"active":spec.servers,
                   "arrivals":processed,"completed":completed,"blocked":blocked,"abandoned":0,
                   "avg_wait_so_far":round(mean(waits),5) if waits else 0.,
                   "utilization_so_far":round(busy_area/(spec.servers*spec.horizon),6)})
    left = processed - completed - blocked
    server_cost = spec.servers * spec.horizon / 60 * spec.server_hour
    waiting_cost = queue_area / 60 * spec.wait_hour
    lost_cost = blocked * spec.lost_cost
    return {"arrivals":processed, "completed":completed,"started":started,
            "blocked":blocked,"admitted":processed-blocked,"unserved_at_close":left,
            "avg_wait":mean(waits) if waits else 0.,"avg_system":mean(systems) if systems else 0.,
            "sla":compliant/(processed-blocked) if processed>blocked else 0.,
            "sla_denominator":"clientes admitidos, incluidos pendientes al cierre",
            "utilization":busy_area/(spec.servers*spec.horizon),
            "avg_queue":queue_area/spec.horizon,"max_queue":max_queue,
            "p_block":blocked/processed if processed else 0.,
            "staff_cost":server_cost,"waiting_cost":waiting_cost,
            "lost_cost":lost_cost,"total_cost":server_cost+waiting_cost+lost_cost,
            "waits":waits,"events":frames,
            "series":[{"t":f["t"],"queue":f["queue"],"busy":f["busy"],
                       "arrivals":f["arrivals"],"completed":f["completed"],
                       "avg_wait":f["avg_wait_so_far"],"utilization":f["utilization_so_far"]}
                      for f in frames]}


_METRICS = ("arrivals","completed","started","blocked","admitted","unserved_at_close",
            "avg_wait","avg_system","sla","utilization","avg_queue","max_queue",
            "p_block","staff_cost","waiting_cost","lost_cost","total_cost")


def evaluate(raw: dict, *, include_runs: bool = True) -> dict:
    spec = validate(raw)
    # D/D/c no produce incertidumbre; no repetir cálculos redundantes.
    n = 1 if spec.mode == "deterministic" else spec.replications
    first = simulate_one(spec, spec.seed)
    compact = lambda run: {k: run[k] for k in _METRICS}
    runs = [compact(first)]
    # Guardar la trayectoria completa únicamente de la réplica mostrada en 3D.
    # Las demás réplicas contribuyen a la estadística, pero no ocupan memoria
    # con listas de eventos y clientes innecesarias.
    for i in range(1, n):
        runs.append(compact(simulate_one(spec, spec.seed + i * 1709)))
    metrics = {k: round(mean(r[k] for r in runs), 6) for k in _METRICS}
    confidence = {}
    for k in ("sla","avg_wait","avg_queue","utilization","p_block","total_cost"):
        vals = [r[k] for r in runs]
        margin = 1.96 * stdev(vals) / math.sqrt(n) if n >= 2 else None
        confidence[k] = {"mean":metrics[k],
                         "low":round(max(0,mean(vals)-margin),6) if margin is not None else None,
                         "high":round(min(1,mean(vals)+margin) if k in ("sla","utilization","p_block")
                                      else mean(vals)+margin,6) if margin is not None else None,
                         "method":"IC exploratorio normal 95%; aproximación asintótica"}
    return {"model":spec.model,"mode":spec.mode,"horizon":spec.horizon,
            "replications_requested":spec.replications,"replications_effective":n,
            "seed":spec.seed,"servers":spec.servers,"capacity":spec.capacity,
            "parameters":dict(raw),"metrics":metrics,"confidence_95":confidence,
            "events":first["events"],"series":first["series"],
            "runs":runs if include_runs else [],
            "selected_replica":1,
            "method":"Eventos discretos, horizonte finito. La primera réplica se visualiza en Three.js."}


def optimize(raw: dict, maximum: int, *, target: float | None = None) -> dict:
    """Búsqueda exhaustiva de dotación fija; mismos seeds por alternativa (CRN)."""
    spec = validate(raw)
    limit = _integer(maximum, "Máximo de servidores", 1, 40)
    objective = spec.sla_target if target is None else _number(target,"SLA",0,1)
    trials = []
    for c in range(1,limit+1):
        if MODELS[spec.model][2] is not None and c != MODELS[spec.model][2]:
            continue
        data = dict(raw)
        data["servers"] = c
        if MODELS[spec.model][3]:
            data["capacity"] = c if MODELS[spec.model][4] else max(c, int(raw.get("capacity", c)))
        result = evaluate(data, include_runs=False)
        met = result["metrics"]
        low = result["confidence_95"]["sla"]["low"]
        # Evitar falsas declaraciones de certeza: cuando no hay réplicas
        # suficientes se informa cumplimiento observado y su incertidumbre.
        feasible = met["sla"] >= objective
        trials.append({"servers":c,"sla":met["sla"],"sla_ci_low":low,
                       "total_cost":met["total_cost"],"avg_wait":met["avg_wait"],
                       "feasible_mean":feasible,
                       "feasible_conservative":low is not None and low >= objective})
    winner = min((row for row in trials if row["feasible_mean"]),
                 key=lambda r:(r["total_cost"],r["servers"]),default=None)
    return {"objective":"menor costo total con SLA medio objetivo",
            "target":objective,"alternatives":trials,"recommended":winner,
            "caveat":"La factibilidad usa la media estimada. Revisar IC y supuestos antes de decidir."}
