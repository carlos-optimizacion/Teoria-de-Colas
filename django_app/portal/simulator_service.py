"""Servicio académico para el simulador interactivo M/M/s.

El alumno define el escenario y Decision Lab devuelve indicadores analíticos,
validación del nivel de servicio y una réplica visual de eventos discretos.
No selecciona ni recomienda automáticamente una dotación.
"""

import math

from queue_core import mms_from_minutes, probability_wait_over
from simulation_core import simulate_visual_mms


def _positive_float(data, key, default):
    value = float(data.get(key, default))
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{key} debe ser un número positivo y finito.")
    return value


def _nonnegative_float(data, key, default):
    value = float(data.get(key, default))
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{key} debe ser un número no negativo y finito.")
    return value


def _probability(data, key, default):
    value = float(data.get(key, default))
    if not math.isfinite(value) or value < 0 or value > 1:
        raise ValueError(f"{key} debe estar entre 0 y 1.")
    return value


def _integer(data, key, default, minimum=1, maximum=200):
    value = int(float(data.get(key, default)))
    if value < minimum or value > maximum:
        raise ValueError(f"{key} debe estar entre {minimum} y {maximum}.")
    return value


def _finite_or_none(value):
    return value if isinstance(value, (int, float)) and math.isfinite(value) else None


def simulator_analysis(data: dict) -> dict:
    """Calcula y simula un escenario definido por el alumno."""
    t_llegada = _positive_float(data, "t_llegada", 8)
    t_atencion = _positive_float(data, "t_atencion", 12)
    servers = _integer(data, "servers", 2, minimum=1, maximum=100)
    horizon = _positive_float(data, "horizon", 60)
    horizon = max(15.0, min(horizon, 240.0))
    sla_threshold = _nonnegative_float(data, "sla_threshold", 10)
    sla_target = _probability(data, "sla_target", 0.90)
    seed = _integer(data, "seed", 2026, minimum=1, maximum=999999999)

    result = mms_from_minutes(t_llegada, t_atencion, servers)
    service_level = 1.0 - probability_wait_over(result, sla_threshold)
    stable = bool(result.get("estable", False))

    analytic = {
        "model": result.get("modelo", "M/M/s"),
        "stable": stable,
        "lambda": _finite_or_none(result.get("lambda")),
        "mu": _finite_or_none(result.get("mu")),
        "servers": servers,
        "rho": _finite_or_none(result.get("rho")),
        "wq_min": _finite_or_none(result.get("Wq", 0.0) * 60.0),
        "w_min": _finite_or_none(result.get("W", 0.0) * 60.0),
        "lq": _finite_or_none(result.get("Lq")),
        "l": _finite_or_none(result.get("L")),
        "p_wait": _finite_or_none(result.get("P_espera")),
        "service_level": service_level,
        "effective_rate": _finite_or_none(result.get("lambda_efectiva", result.get("lambda"))),
        "sla_threshold": sla_threshold,
        "sla_target": sla_target,
        "meets_service_level": stable and service_level >= sla_target,
    }

    visual = simulate_visual_mms(
        t_llegada,
        t_atencion,
        servers,
        horizon_min=horizon,
        seed=seed,
    )

    if not stable:
        status = {
            "tone": "danger",
            "title": "Escenario inestable",
            "message": "La capacidad media no alcanza para absorber la demanda. En estado estacionario, la cola y la espera no tienen un promedio finito.",
        }
    elif analytic["meets_service_level"]:
        status = {
            "tone": "success",
            "title": "Escenario estable y meta de servicio cumplida",
            "message": f"El nivel de servicio calculado alcanza la meta definida de {sla_target * 100:.1f}% para una espera máxima de {sla_threshold:g} min.",
        }
    else:
        status = {
            "tone": "info",
            "title": "Escenario estable, pero la meta de servicio no se cumple",
            "message": f"La configuración es estable, aunque el nivel de servicio queda por debajo de la meta de {sla_target * 100:.1f}% para {sla_threshold:g} min.",
        }

    indicator_help = [
        {
            "key": "rho",
            "symbol": "ρ",
            "name": "Utilización",
            "definition": "Fracción de la capacidad total que está ocupada en promedio.",
            "reading": "Cuando se acerca a 100%, queda poco margen frente a la variabilidad y la espera puede crecer de forma no lineal.",
        },
        {
            "key": "wq_min",
            "symbol": "Wq",
            "name": "Espera promedio en cola",
            "definition": "Minutos promedio que un cliente permanece esperando antes de iniciar servicio.",
            "reading": "Mide directamente la experiencia de espera antes de ser atendido.",
        },
        {
            "key": "lq",
            "symbol": "Lq",
            "name": "Clientes promedio en cola",
            "definition": "Número promedio de clientes que están esperando, sin contar a quienes ya están en servicio.",
            "reading": "Ayuda a dimensionar espacio físico, congestión visible y carga operativa de la cola.",
        },
        {
            "key": "p_wait",
            "symbol": "P(espera)",
            "name": "Probabilidad de esperar",
            "definition": "Probabilidad de que un cliente encuentre todos los servidores ocupados y tenga que hacer cola.",
            "reading": "Puede interpretarse como cuántos de cada 100 clientes probablemente tendrán que esperar.",
        },
        {
            "key": "service_level",
            "symbol": "NS",
            "name": "Nivel de servicio",
            "definition": f"Probabilidad de que la espera sea menor o igual a {sla_threshold:g} minutos.",
            "reading": "Permite validar el escenario contra una meta operativa explícita, no solo contra un promedio de espera.",
        },
        {
            "key": "w_min",
            "symbol": "W",
            "name": "Tiempo promedio en el sistema",
            "definition": "Tiempo total promedio desde que el cliente llega hasta que termina su atención.",
            "reading": "Incluye tanto la espera como el tiempo efectivo de servicio.",
        },
        {
            "key": "effective_rate",
            "symbol": "λe",
            "name": "Tasa efectiva",
            "definition": "Clientes por hora que el modelo admite al sistema; en M/M/s sin bloqueo coincide con la tasa de llegada.",
            "reading": "Sirve como referencia del flujo que debe absorber la operación en el escenario evaluado.",
        },
    ]

    return {
        "analytic": analytic,
        "visual": visual,
        "status": status,
        "indicator_help": indicator_help,
    }
