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
    """Prohíbe recomendaciones monetarias entre horizontes distintos."""
    if len(items) < 2:
        return False, "Selecciona por lo menos dos corridas."
    if len({x["horizon_min"] for x in items}) > 1:
        return False, "Horizontes diferentes: los costos totales no son directamente comparables."
    if len({x["sector"] for x in items}) > 1:
        return False, "Sectores diferentes: no se debe recomendar una dotación comparando sus costos."
    return True, "Escenarios con sector y horizonte comparables; revisa los demás supuestos."
