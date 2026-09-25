"""Motor matemático compartido para la plataforma de Teoría de Colas.

Convenciones:
- lambda (lam) y mu se expresan en eventos por hora.
- W y Wq se devuelven en horas.
- L y Lq se expresan en clientes/unidades promedio.
- Las funciones *_from_minutes aceptan datos operativos en minutos.

El módulo no depende de Streamlit ni de pandas para que pueda probarse de forma
independiente y reutilizarse en cualquier interfaz.
"""

import math


def rates_from_minutes(t_llegada_min: float, t_atencion_min: float):
    """Convierte tiempos promedio en minutos a tasas por hora."""
    if t_llegada_min <= 0 or t_atencion_min <= 0:
        raise ValueError("Los tiempos deben ser mayores que cero.")
    return 60.0 / t_llegada_min, 60.0 / t_atencion_min


def erlang_b(a: float, s: int) -> float:
    """Calcula Erlang B mediante recurrencia estable numéricamente."""
    if a < 0 or s < 1:
        raise ValueError("La carga ofrecida debe ser no negativa y s >= 1.")
    b = 1.0
    for n in range(1, s + 1):
        b = (a * b) / (n + a * b) if a > 0 else 0.0
    return b


def mms(lam: float, mu: float, s: int):
    """Modelo M/M/s (M/M/1 cuando s=1) usando Erlang C.

    Para rho >= 1 el sistema de capacidad infinita es inestable y las medidas
    de congestión de estado estacionario se reportan como infinito.
    """
    if lam <= 0 or mu <= 0 or s < 1:
        raise ValueError("λ y μ deben ser positivos y s debe ser al menos 1.")

    rho = lam / (s * mu)
    base = {
        "modelo": "M/M/1" if s == 1 else "M/M/s",
        "lambda": lam,
        "mu": mu,
        "s": s,
        "rho": rho,
        "P_bloqueo": 0.0,
        "lambda_efectiva": lam,
    }

    if rho >= 1:
        return {
            **base,
            "estable": False,
            "L": float("inf"),
            "Lq": float("inf"),
            "W": float("inf"),
            "Wq": float("inf"),
            "P_espera": 1.0,
        }

    # Erlang C calculado a partir de Erlang B. Esta forma evita factoriales y
    # potencias grandes, por lo que es más robusta para valores altos de s.
    a = lam / mu
    b = erlang_b(a, s)
    p_espera = b / (1.0 - rho + rho * b)

    Lq = p_espera * rho / (1.0 - rho)
    Wq = Lq / lam
    W = Wq + 1.0 / mu
    L = lam * W

    return {
        **base,
        "estable": True,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "P_espera": p_espera,
    }


def mms_from_minutes(t_llegada_min: float, t_atencion_min: float, s: int):
    lam, mu = rates_from_minutes(t_llegada_min, t_atencion_min)
    return mms(lam, mu, s)


def probability_wait_over(result: dict, threshold_minutes: float) -> float:
    """P(Wq > t) para un sistema M/M/s estable mediante Erlang C.

    El resultado debe provenir de :func:`mms` o :func:`mms_from_minutes`.
    """
    if threshold_minutes < 0:
        raise ValueError("El umbral de espera no puede ser negativo.")
    if not result.get("estable", False):
        return 1.0

    required = ("lambda", "mu", "s", "P_espera")
    if any(k not in result for k in required):
        raise ValueError("El resultado no contiene los parámetros requeridos de M/M/s.")

    rate = result["s"] * result["mu"] - result["lambda"]
    threshold_hours = threshold_minutes / 60.0
    return result["P_espera"] * math.exp(-rate * threshold_hours)


def mmsk(lam: float, mu: float, s: int, k: int):
    """Modelo M/M/s/K con capacidad total finita K."""
    if lam <= 0 or mu <= 0 or s < 1:
        raise ValueError("λ y μ deben ser positivos y s debe ser al menos 1.")
    if k < s:
        raise ValueError("K debe ser mayor o igual al número de servidores.")

    weights = [1.0]
    for n in range(1, k + 1):
        salida = min(n, s) * mu
        weights.append(weights[-1] * lam / salida)
        if max(weights) > 1e180:
            escala = max(weights)
            weights = [w / escala for w in weights]

    total = sum(weights)
    probs = [w / total for w in weights]
    p_bloqueo = probs[-1]
    lam_eff = lam * (1.0 - p_bloqueo)
    L = sum(n * probs[n] for n in range(k + 1))
    ocupados = lam_eff / mu
    Lq = max(0.0, L - ocupados)
    W = L / lam_eff if lam_eff > 0 else float("inf")
    Wq = Lq / lam_eff if lam_eff > 0 else float("inf")
    rho_ef = ocupados / s

    prob_estados_espera = sum(probs[s:k]) if k > s else 0.0
    p_espera_admitido = (
        prob_estados_espera / (1.0 - p_bloqueo)
        if p_bloqueo < 1.0
        else 1.0
    )

    return {
        "modelo": "M/M/1/K" if s == 1 else "M/M/s/K",
        "estable": True,
        "lambda": lam,
        "mu": mu,
        "s": s,
        "K": k,
        "rho": rho_ef,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "P_espera": p_espera_admitido,
        "P_bloqueo": p_bloqueo,
        "lambda_efectiva": lam_eff,
        "probs": probs,
    }


def mmsk_from_minutes(t_llegada_min: float, t_atencion_min: float, s: int, k: int):
    lam, mu = rates_from_minutes(t_llegada_min, t_atencion_min)
    return mmsk(lam, mu, s, k)


def mg1_from_minutes(t_llegada_min: float, media_servicio_min: float, cv: float):
    """Modelo M/G/1 mediante Pollaczek-Khinchine.

    El coeficiente de variación (CV) representa la desviación estándar del
    servicio dividida entre su media. W y Wq se devuelven en horas para mantener
    la misma convención que el resto del motor.
    """
    if t_llegada_min <= 0 or media_servicio_min <= 0:
        raise ValueError("Los tiempos deben ser mayores que cero.")
    if cv < 0:
        raise ValueError("El coeficiente de variación no puede ser negativo.")

    lam = 60.0 / t_llegada_min
    es = media_servicio_min / 60.0
    var_s = (cv * es) ** 2
    es2 = var_s + es**2
    rho = lam * es

    base = {
        "modelo": "M/G/1",
        "lambda": lam,
        "ES": es,
        "cv": cv,
        "var": var_s,
        "rho": rho,
        "s": 1,
    }

    if rho >= 1:
        return {
            **base,
            "estable": False,
            "L": float("inf"),
            "Lq": float("inf"),
            "W": float("inf"),
            "Wq": float("inf"),
        }

    Wq = lam * es2 / (2.0 * (1.0 - rho))
    Lq = lam * Wq
    W = Wq + es
    L = lam * W

    return {
        **base,
        "estable": True,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
    }


def economic_cost(
    result: dict,
    s: int,
    costo_operador_h: float,
    costo_espera_cliente_h: float,
    costo_cliente_perdido: float = 0.0,
):
    """Costo horario de capacidad, espera y clientes bloqueados/perdidos."""
    if s < 1:
        raise ValueError("s debe ser al menos 1.")
    if costo_operador_h < 0 or costo_espera_cliente_h < 0 or costo_cliente_perdido < 0:
        raise ValueError("Los costos no pueden ser negativos.")

    costo_personal = s * costo_operador_h
    perdidos_h = max(0.0, result["lambda"] - result["lambda_efectiva"])
    costo_perdida = perdidos_h * costo_cliente_perdido

    if not result.get("estable", False) or not math.isfinite(result["Lq"]):
        return {
            "personal": costo_personal,
            "espera": float("inf"),
            "perdidos_h": perdidos_h,
            "perdida": costo_perdida,
            "total": float("inf"),
        }

    costo_espera = result["Lq"] * costo_espera_cliente_h
    return {
        "personal": costo_personal,
        "espera": costo_espera,
        "perdidos_h": perdidos_h,
        "perdida": costo_perdida,
        "total": costo_personal + costo_espera + costo_perdida,
    }


def evaluate_mms_capacity(
    t_llegada_min: float,
    t_atencion_min: float,
    max_servers: int,
    costo_operador_h: float = 0.0,
    costo_espera_cliente_h: float = 0.0,
    meta_wq_min: float | None = None,
    meta_p_espera: float | None = None,
):
    """Evalúa escenarios de 1..max_servers sin depender de la interfaz."""
    if max_servers < 1:
        raise ValueError("max_servers debe ser al menos 1.")
    if meta_wq_min is not None and meta_wq_min < 0:
        raise ValueError("La meta de espera no puede ser negativa.")
    if meta_p_espera is not None and not 0 <= meta_p_espera <= 1:
        raise ValueError("meta_p_espera debe estar entre 0 y 1.")

    escenarios = []
    for s in range(1, max_servers + 1):
        r = mms_from_minutes(t_llegada_min, t_atencion_min, s)
        c = economic_cost(r, s, costo_operador_h, costo_espera_cliente_h)
        wq_min = r["Wq"] * 60.0 if math.isfinite(r["Wq"]) else float("inf")
        cumple_wq = meta_wq_min is None or wq_min <= meta_wq_min
        cumple_p = meta_p_espera is None or r["P_espera"] <= meta_p_espera
        escenarios.append(
            {
                "servers": s,
                "stable": r["estable"],
                "rho": r["rho"],
                "p_wait": r["P_espera"],
                "Lq": r["Lq"],
                "Wq_min": wq_min,
                "W_min": r["W"] * 60.0 if math.isfinite(r["W"]) else float("inf"),
                "cost_staff": c["personal"],
                "cost_wait": c["espera"],
                "cost_total": c["total"],
                "meets_service": r["estable"] and cumple_wq and cumple_p,
            }
        )
    return escenarios


def recommend_mms_capacity(*args, **kwargs):
    """Devuelve (escenarios, recomendado) según meta de servicio y costo total."""
    escenarios = evaluate_mms_capacity(*args, **kwargs)
    candidatos = [e for e in escenarios if e["meets_service"]]
    if candidatos:
        recomendado = min(candidatos, key=lambda e: (e["cost_total"], e["servers"]))
    else:
        estables = [e for e in escenarios if e["stable"]]
        recomendado = min(estables, key=lambda e: (e["Wq_min"], e["cost_total"])) if estables else escenarios[-1]
    return escenarios, recomendado


def dd1_sequence(t_llegada_min: float, t_atencion_min: float, n: int = 12):
    """Secuencia determinista D/D/1 para fines didácticos."""
    if t_llegada_min <= 0 or t_atencion_min <= 0 or n < 1:
        raise ValueError("Parámetros inválidos.")
    filas = []
    fin_anterior = 0.0
    for i in range(1, n + 1):
        llegada = (i - 1) * t_llegada_min
        inicio = max(llegada, fin_anterior)
        espera = inicio - llegada
        fin = inicio + t_atencion_min
        filas.append(
            {
                "Cliente": i,
                "Llegada (min)": llegada,
                "Inicio atención (min)": inicio,
                "Espera (min)": espera,
                "Salida (min)": fin,
            }
        )
        fin_anterior = fin
    return filas
