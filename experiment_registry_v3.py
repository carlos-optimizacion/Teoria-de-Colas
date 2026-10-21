"""Registro de experimentos Decision Lab 3.0.

Interfaz común para las áreas Simulación, Desafíos, Red de colas y Análisis.
El registro vive en st.session_state; no afirma persistencia de nube.
Conserva resultados consolidados y procedencia, no listas de clientes ni PII.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any

MAX_SNAPSHOTS = 30
EXCLUDED_SOURCE_FIELDS = {"arrival_samples", "service_samples", "exact_arrivals", "raw_records"}


def _safe(value: Any) -> Any:
    """Representación JSON sin serializadores opcionales de frameworks."""
    if isinstance(value, dict):
        return {str(k): _safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(v) for v in value]
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Las métricas no pueden contener NaN o infinito")
        return value
    raise ValueError(f"Tipo de dato no permitido: {type(value).__name__}")


def snapshot_experiment(raw: dict, result: dict, sector: str) -> dict:
    if not isinstance(raw, dict) or not isinstance(result, dict):
        raise ValueError("Configuración y resultado deben ser objetos")
    metrics = result.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        raise ValueError("La corrida no incluye métricas consolidadas")
    safe_params = {
        key: _safe(value)
        for key, value in raw.items()
        if key not in EXCLUDED_SOURCE_FIELDS
    }
    for key in ("arrival_samples", "service_samples", "exact_arrivals"):
        if key in raw:
            safe_params[key + "_count"] = len(raw[key])
    payload = {
        "source": "queue_v3",
        "sector": sector,
        "model": str(result["model"]),
        "mode": str(result["mode"]),
        "horizon_min": int(result["horizon"]),
        "replications": int(result["replications_effective"]),
        "seed": int(result["seed"]),
        "servers": int(result["servers"]),
        "capacity": result["capacity"],
        "metrics": _safe(metrics),
        "parameters": safe_params,
        "method": str(result.get("method", "")),
        "confidence_95": _safe(result.get("confidence_95", {})),
    }
    if payload["horizon_min"] < 1 or payload["replications"] < 1:
        raise ValueError("El horizonte y las réplicas deben ser positivos")
    serial = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    payload["id"] = hashlib.sha256(serial.encode("utf-8")).hexdigest()[:12]
    return payload


def register_experiment(registry: list[dict], item: dict, max_items: int = MAX_SNAPSHOTS) -> list[dict]:
    if not isinstance(registry, list) or not isinstance(item, dict) or not item.get("id"):
        raise ValueError("Registro e identificador inválidos")
    if not 1 <= max_items <= 500:
        raise ValueError("Límite de corridas fuera de rango")
    updated = [old for old in registry if old.get("id") != item["id"]]
    updated.append(item)
    return updated[-max_items:]


def comparison_rows(items: list[dict]) -> list[dict]:
    rows = []
    for item in items:
        metrics = item["metrics"]
        rows.append({
            "ID": item["id"],
            "Sector": item["sector"],
            "Modelo": item["model"],
            "Modalidad": item["mode"],
            "Horizonte (min)": item["horizon_min"],
            "Réplicas": item["replications"],
            "Servidores": item["servers"],
            "Wq (min)": metrics.get("avg_wait"),
            "Lq (clientes)": metrics.get("avg_queue"),
            "Utilización (%)": round(metrics["utilization"] * 100, 2) if "utilization" in metrics else None,
            "SLA (%)": round(metrics["sla"] * 100, 2) if "sla" in metrics else None,
            "Rechazados": metrics.get("blocked"),
            "Costo total (S/)": metrics.get("total_cost"),
        })
    return rows


def comparable(items: list[dict]) -> tuple[bool, str]:
    """Guardas de comparabilidad gerencial de experimentos independientes.

    Comparar tablas es libre, pero calcular una recomendación de menor costo
    exige el mismo problema base. Dotación y capacidad son variables de decisión.
    """
    if len(items)<2:
        return False,"Selecciona por lo menos dos corridas."
    same={
        "sector":"sectores","horizon_min":"horizontes","model":"modelos",
        "mode":"modalidades","source":"motores",
    }
    for key,label in same.items():
        if len({x.get(key) for x in items})>1:
            return False,f"Comparación no homogénea: {label} distintos."
    fields={
        "arrival_mean":"demanda de llegada","service_mean":"tiempo medio de atención",
        "arrival_dist":"distribución de llegada","service_dist":"distribución del servicio",
        "arrival_cv":"variabilidad de llegada","service_cv":"variabilidad del servicio",
        "sla_min":"umbral SLA","sla_target":"meta SLA",
        "server_hour":"costo del servidor","wait_hour":"costo de espera",
        "lost_cost":"penalidad por pérdida",
    }
    for key,label in fields.items():
        vals=[x.get("parameters",{}).get(key) for x in items]
        if len({repr(v) for v in vals})>1:
            return False,f"Supuestos incompatibles: {label} diferentes."
    # Prohibir mezclar datos históricos originados en poblaciones distintas.
    provenance=[x.get("parameters",{}).get("empirical_quality",{}).get("source_sha256")
                for x in items]
    if len({str(x) for x in provenance})>1:
        return False,"Fuentes históricas diferentes: la comparación exige explicar sus poblaciones."
    return True,"Problema base comparable: sector, modelo, demanda, servicio, SLA y costos coinciden."


def recommend_comparison(items: list[dict]) -> dict:
    """Mejor costo observado SOLO entre corridas que satisfacen el SLA del caso."""
    valid,reason=comparable(items)
    if not valid:
        return {"valid":False,"reason":reason,"target":None,"feasible":[],
                "recommended":None}
    target=items[0].get("parameters",{}).get("sla_target",.90)
    if target is None:
        target=.90
    target=float(target)
    if not 0<=target<=1:
        raise ValueError("Meta SLA fuera de rango")
    available=[]
    for item in items:
        m=item["metrics"]
        cost=float(m["total_cost"]);sla=float(m["sla"])
        if not (math.isfinite(cost) and math.isfinite(sla) and cost>=0 and 0<=sla<=1):
            raise ValueError("Métricas de costo o SLA inválidas")
        if sla>=target:
            available.append(item)
    winner=min(available,key=lambda item:(item["metrics"]["total_cost"],item["id"])) if available else None
    return {
        "valid":True,"reason":reason,"target":target,
        "feasible":[x["id"] for x in available],
        "recommended":winner["id"] if winner else None,
        "cost":winner["metrics"]["total_cost"] if winner else None,
        "sla":winner["metrics"]["sla"] if winner else None,
        "caveat":"Mínimo costo observado ENTRE las corridas y restricciones evaluadas; "
                 "no se demuestra óptimo global ni significancia estadística."
    }
