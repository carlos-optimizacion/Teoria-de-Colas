"""Servicios de simulación visual para el flujo End-to-End."""

from simulation_core import simulate_visual_mms


def visual_end_to_end_payload(data: dict, analysis: dict) -> dict:
    t_llegada = float(data.get("t_llegada", 8))
    t_atencion = float(data.get("t_atencion", 12))
    horizon = float(data.get("visual_horizon", 60))
    horizon = max(15.0, min(horizon, 240.0))
    seed = int(float(data.get("visual_seed", 2026)))

    current_servers = int(analysis["actual"]["servers"])
    recommended_servers = int(analysis["recommended"]["servers"])

    current = simulate_visual_mms(
        t_llegada,
        t_atencion,
        current_servers,
        horizon_min=horizon,
        seed=seed,
    )
    recommended = simulate_visual_mms(
        t_llegada,
        t_atencion,
        recommended_servers,
        horizon_min=horizon,
        seed=seed,
    )

    return {
        "horizon_min": horizon,
        "seed": seed,
        "current": current,
        "recommended": recommended,
        "same_base_randomness": True,
        "note": (
            "Ambos escenarios usan la misma semilla y flujos aleatorios separados para "
            "llegadas y tiempos de servicio, de modo que la comparación visual se realiza "
            "sobre una secuencia base equivalente de clientes."
        ),
    }
