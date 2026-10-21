"""Contrato analítico de redes multietapa Decision Lab 3.0.

No considera estaciones independientes: conserva el enrutamiento del mismo
cliente entre etapas y no afirma equivalencia con un M/M/c aislado. Cada
réplica tiene semilla controlada; la trayectoria es la de la primera réplica.
"""
from __future__ import annotations

import math
from statistics import mean, stdev
from .network_engine import simulate_network

NETWORK_MAX_REPS=40
NETWORK_METRICS=("arrivals","completed","in_system_at_close","throughput_rate","avg_system")
STAGE_METRICS=("arrived","completed","in_stage_at_close","avg_wait","avg_queue",
               "utilization","max_queue","started")


def evaluate_network(raw: dict) -> dict:
    if not isinstance(raw,dict):
        raise ValueError("La red requiere un objeto de configuración")
    reps=raw.get("replications",1)
    if isinstance(reps,bool) or not isinstance(reps,int) or not 1<=reps<=NETWORK_MAX_REPS:
        raise ValueError("Réplicas de red: un entero de 1 a 40")
    first=simulate_network(raw)
    runs=[first]
    for i in range(1,reps):
        next_seed=((first["seed"]-1+1709*i)%999999999)+1
        runs.append(simulate_network({**raw,"seed":next_seed}))
    aggregate={
        key:round(mean(r[key] for r in runs),6)
        for key in NETWORK_METRICS
    }
    conf={}
    for key in ("throughput_rate","avg_system","completed","in_system_at_close"):
        v=[r[key] for r in runs]
        margin=1.96*stdev(v)/math.sqrt(reps) if reps>1 else None
        conf[key]={"mean":aggregate[key],
                   "low":round(max(0,mean(v)-margin),6) if margin is not None else None,
                   "high":round(mean(v)+margin,6) if margin is not None else None,
                   "method":"IC exploratorio normal 95%; réplicas independientes"}
    stage_summary=[]
    for i,stage in enumerate(first["stages"]):
        row={"name":stage["name"],"servers":stage["servers"],
             "service_min":stage["service_min"]}
        for key in STAGE_METRICS:
            row[key]=round(mean(r["stages"][i][key] for r in runs),6)
        # Bottleneck means high occupancy / queue, not a causal proof.
        stage_summary.append(row)
    bottleneck_idx=max(range(len(stage_summary)),
                       key=lambda i:(stage_summary[i]["utilization"],
                                     stage_summary[i]["avg_queue"]))
    compact_runs=[{
        "replica":i+1,"seed":r["seed"],
        **{key:r[key] for key in NETWORK_METRICS}
    } for i,r in enumerate(runs)]
    for r in runs:
        assert r["arrivals"]==r["completed"]+r["in_system_at_close"]
        assert all(x["arrived"]==x["completed"]+x["in_stage_at_close"]
                   for x in r["stages"])
    return {
        "engine":"network_engine","integration_contract":"v3",
        "model":"Tándem M/M/c","mode":"parametric","horizon":first["horizon"],
        "seed":first["seed"],"replications_requested":reps,
        "replications_effective":reps,
        "metrics":aggregate,"confidence_95":conf,
        "stages":stage_summary,"bottleneck_index":bottleneck_idx,
        "runs":compact_runs,"frames":first["frames"],
        "parameters":dict(raw),
        "method":"Red tándem FCFS, llegadas Poisson, servicios exponenciales "
                 "por etapa, sin bloqueo ni abandono; horizonte finito. "
                 "Una única trayectoria se visualiza. Cuello de botella "
                 "sugerido por máxima utilización media, no por causalidad demostrada.",
    }
