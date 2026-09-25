import math


def rates_from_minutes(t_llegada_min: float, t_atencion_min: float):
    if t_llegada_min <= 0 or t_atencion_min <= 0:
        raise ValueError("Los tiempos deben ser mayores que cero.")
    return 60.0 / t_llegada_min, 60.0 / t_atencion_min


def mms(lam: float, mu: float, s: int):
    if lam <= 0 or mu <= 0 or s < 1:
        raise ValueError("λ y μ deben ser positivos y s debe ser al menos 1.")

    rho = lam / (s * mu)
    if rho >= 1:
        return {
            "modelo": "M/M/1" if s == 1 else "M/M/s",
            "estable": False,
            "lambda": lam,
            "mu": mu,
            "s": s,
            "rho": rho,
            "L": float("inf"),
            "Lq": float("inf"),
            "W": float("inf"),
            "Wq": float("inf"),
            "P_espera": 1.0,
            "P_bloqueo": 0.0,
            "lambda_efectiva": lam,
        }

    if s == 1:
        L = rho / (1 - rho)
        Lq = rho**2 / (1 - rho)
        W = 1 / (mu - lam)
        Wq = Lq / lam
        p_espera = rho
    else:
        a = lam / mu
        termino = 1.0
        suma = 1.0
        for n in range(1, s):
            termino *= a / n
            suma += termino
        termino_s = termino * a / s
        cola = termino_s / (1 - rho)
        p0 = 1 / (suma + cola)
        p_espera = cola * p0
        Lq = p_espera * rho / (1 - rho)
        L = Lq + a
        Wq = Lq / lam
        W = Wq + 1 / mu

    return {
        "modelo": "M/M/1" if s == 1 else "M/M/s",
        "estable": True,
        "lambda": lam,
        "mu": mu,
        "s": s,
        "rho": rho,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "P_espera": p_espera,
        "P_bloqueo": 0.0,
        "lambda_efectiva": lam,
    }


def mms_from_minutes(t_llegada_min: float, t_atencion_min: float, s: int):
    lam, mu = rates_from_minutes(t_llegada_min, t_atencion_min)
    return mms(lam, mu, s)


def mmsk(lam: float, mu: float, s: int, k: int):
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
    lam_eff = lam * (1 - p_bloqueo)
    L = sum(n * probs[n] for n in range(k + 1))
    ocupados = lam_eff / mu
    Lq = max(0.0, L - ocupados)
    W = L / lam_eff if lam_eff > 0 else float("inf")
    Wq = Lq / lam_eff if lam_eff > 0 else float("inf")
    rho_ef = ocupados / s

    prob_estados_espera = sum(probs[s:k]) if k > s else 0.0
    p_espera_admitido = prob_estados_espera / (1 - p_bloqueo) if p_bloqueo < 1 else 1.0

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


def economic_cost(result, s: int, costo_operador_h: float, costo_espera_cliente_h: float, costo_cliente_perdido: float = 0.0):
    costo_personal = s * costo_operador_h
    costo_espera = 0.0 if not math.isfinite(result["Lq"]) else result["Lq"] * costo_espera_cliente_h
    perdidos_h = max(0.0, result["lambda"] - result["lambda_efectiva"])
    costo_perdida = perdidos_h * costo_cliente_perdido
    return {
        "personal": costo_personal,
        "espera": costo_espera,
        "perdidos_h": perdidos_h,
        "perdida": costo_perdida,
        "total": costo_personal + costo_espera + costo_perdida,
    }


def dd1_sequence(t_llegada_min: float, t_atencion_min: float, n: int = 12):
    if t_llegada_min <= 0 or t_atencion_min <= 0 or n < 1:
        raise ValueError("Parámetros inválidos.")
    filas = []
    fin_anterior = 0.0
    for i in range(1, n + 1):
        llegada = (i - 1) * t_llegada_min
        inicio = max(llegada, fin_anterior)
        espera = inicio - llegada
        fin = inicio + t_atencion_min
        filas.append({
            "Cliente": i,
            "Llegada (min)": llegada,
            "Inicio atención (min)": inicio,
            "Espera (min)": espera,
            "Salida (min)": fin,
        })
        fin_anterior = fin
    return filas
