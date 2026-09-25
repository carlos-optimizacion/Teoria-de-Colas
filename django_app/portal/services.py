"""Capa de aplicación Django sobre los motores compartidos de Decision Lab."""

import csv
import io
import math
from statistics import mean, stdev

from interpretation_core import (
    interpret_dd1,
    interpret_economic,
    interpret_erlang_b,
    interpret_mg1,
    interpret_mm1,
    interpret_mms,
    interpret_mmsk,
    marginal_mms_analysis,
)
from queue_core import (
    dd1_sequence,
    economic_cost,
    erlang_b,
    evaluate_mms_capacity,
    mg1_from_minutes,
    mms_from_minutes,
    mmsk_from_minutes,
    probability_wait_over,
    rates_from_minutes,
)
from simulation_core import simulate_queue


MODEL_CATALOG = {
    "mm1": {
        "name": "M/M/1",
        "subtitle": "Una cola, un servidor y capacidad de espera ilimitada.",
        "formula": "ρ = λ/μ · Wq = λ/[μ(μ−λ)]",
        "assumption": "Llegadas Poisson, servicio exponencial, FIFO y un servidor.",
    },
    "mms": {
        "name": "M/M/s",
        "subtitle": "Una cola compartida por múltiples servidores equivalentes.",
        "formula": "ρ = λ/(sμ) · Erlang C",
        "assumption": "Llegadas Poisson, servicios exponenciales y servidores equivalentes.",
    },
    "mmsk": {
        "name": "M/M/s/K",
        "subtitle": "Múltiples servidores con capacidad total finita K.",
        "formula": "K = clientes máximos dentro del sistema",
        "assumption": "Cuando hay K clientes, nuevas llegadas son bloqueadas.",
    },
    "mm1c": {
        "name": "M/M/1 con espera limitada",
        "subtitle": "Un servidor y c plazas de espera; internamente K = c + 1.",
        "formula": "K = c + 1",
        "assumption": "Se conserva el alias c para enseñanza, pero el motor usa K total.",
    },
    "mmstotal": {
        "name": "M/M/s con capacidad total",
        "subtitle": "s servidores y un máximo K de clientes dentro del sistema.",
        "formula": "K ≥ s",
        "assumption": "La capacidad total incluye clientes en servicio y en espera.",
    },
    "erlangb": {
        "name": "M/M/s/s · Erlang B",
        "subtitle": "Sistema de pérdidas: si todos los servidores están ocupados, no hay cola.",
        "formula": "B(s,a) · a = λ/μ",
        "assumption": "No existe sala de espera; congestión se manifiesta como bloqueo.",
    },
    "mg1": {
        "name": "M/G/1",
        "subtitle": "Un servidor con tiempos de servicio generales y variabilidad explícita.",
        "formula": "Wq = λE[S²] / 2(1−ρ)",
        "assumption": "Pollaczek–Khinchine usa media y segundo momento del servicio.",
    },
    "dd1": {
        "name": "D/D/1",
        "subtitle": "Llegadas y servicios deterministas para estudiar sincronización.",
        "formula": "S ≤ T ⇒ no acumulación ideal",
        "assumption": "Sin variabilidad; permite aislar el desbalance estructural.",
    },
}

CASES = [
    {"name": "Urgencias ambulatorias", "sector": "Salud", "model": "mms", "t_llegada": 6, "t_atencion": 14, "servers": 3, "question": "¿La dotación absorbe la demanda y cuánto espera el paciente?"},
    {"name": "Ventanillas bancarias", "sector": "Servicios", "model": "mms", "t_llegada": 4, "t_atencion": 10, "servers": 3, "question": "¿Qué cambia al abrir o cerrar una ventanilla?"},
    {"name": "Puesto de inspección", "sector": "Producción", "model": "dd1", "t_llegada": 8, "t_atencion": 9, "servers": 1, "question": "¿El atraso proviene de variabilidad o de falta estructural de capacidad?"},
]


def _finite(value):
    return value if isinstance(value, (int, float)) and math.isfinite(value) else None


def _f(data, key, default):
    value = float(data.get(key, default))
    if not math.isfinite(value):
        raise ValueError(f"{key} debe ser finito.")
    return value


def _i(data, key, default):
    return int(float(data.get(key, default)))


def _pack_result(result):
    return {
        "model": result.get("modelo", ""),
        "stable": result.get("estable", True),
        "lambda": _finite(result.get("lambda")),
        "mu": _finite(result.get("mu")),
        "servers": result.get("s", 1),
        "capacity": result.get("K"),
        "rho": _finite(result.get("rho")),
        "p_wait": _finite(result.get("P_espera", 0.0)),
        "p_block": _finite(result.get("P_bloqueo", 0.0)),
        "effective_rate": _finite(result.get("lambda_efectiva", result.get("lambda"))),
        "wq_min": _finite(result.get("Wq", 0.0) * 60.0),
        "w_min": _finite(result.get("W", 0.0) * 60.0),
        "lq": _finite(result.get("Lq", 0.0)),
        "l": _finite(result.get("L", 0.0)),
        "probs": result.get("probs"),
    }


def erlang_b_result(t_llegada, t_atencion, servers):
    lam, mu = rates_from_minutes(t_llegada, t_atencion)
    offered = lam / mu
    blocking = erlang_b(offered, servers)
    lam_eff = lam * (1.0 - blocking)
    avg_busy = lam_eff / mu
    rho = avg_busy / servers
    return {
        "modelo": "M/M/s/s",
        "estable": True,
        "lambda": lam,
        "mu": mu,
        "s": servers,
        "K": servers,
        "rho": rho,
        "L": avg_busy,
        "Lq": 0.0,
        "W": 1.0 / mu,
        "Wq": 0.0,
        "P_espera": 0.0,
        "P_bloqueo": blocking,
        "lambda_efectiva": lam_eff,
        "B": blocking,
        "lambda_eff": lam_eff,
        "ocupacion": rho,
    }


def calculate_model(data, run_simulation=True):
    key = data.get("model", "mms")
    if key not in MODEL_CATALOG:
        raise ValueError("Modelo no soportado.")
    t_llegada = _f(data, "t_llegada", 10)
    t_atencion = _f(data, "t_atencion", 8)
    horizon = max(60.0, min(_f(data, "horizon", 480), 1440.0))
    replications = max(1, min(_i(data, "replications", 30), 200))
    simulation = None
    sequence = None
    note = None

    if key == "mm1":
        result = mms_from_minutes(t_llegada, t_atencion, 1)
        interpretation = interpret_mm1(result)
        sim_args = {"servers": 1}
    elif key == "mms":
        servers = max(1, _i(data, "servers", 2))
        result = mms_from_minutes(t_llegada, t_atencion, servers)
        interpretation = interpret_mms(result, servers)
        sim_args = {"servers": servers}
    elif key in {"mmsk", "mmstotal"}:
        servers = max(1, _i(data, "servers", 2))
        capacity = max(servers, _i(data, "capacity", max(servers + 4, 6)))
        result = mmsk_from_minutes(t_llegada, t_atencion, servers, capacity)
        interpretation = interpret_mmsk(result)
        sim_args = {"servers": servers, "capacity": capacity}
    elif key == "mm1c":
        waiting_places = max(0, _i(data, "waiting_places", 5))
        capacity = waiting_places + 1
        result = mmsk_from_minutes(t_llegada, t_atencion, 1, capacity)
        interpretation = interpret_mmsk(result)
        sim_args = {"servers": 1, "capacity": capacity}
        note = f"c={waiting_places} plazas de espera se normaliza como K={capacity} de capacidad total."
    elif key == "erlangb":
        servers = max(1, _i(data, "servers", 3))
        result = erlang_b_result(t_llegada, t_atencion, servers)
        interpretation = interpret_erlang_b(result, servers)
        sim_args = {"servers": servers, "capacity": servers}
    elif key == "mg1":
        cv = max(0.0, _f(data, "cv", 1.0))
        result = mg1_from_minutes(t_llegada, t_atencion, cv)
        result["P_espera"] = min(1.0, max(0.0, result["rho"]))
        result["P_bloqueo"] = 0.0
        result["lambda_efectiva"] = result["lambda"]
        interpretation = interpret_mg1(result, cv, time_unit="hours")
        sim_args = {"servers": 1, "service_distribution": "gamma", "service_cv": cv}
        note = "La simulación usa una Gamma con la misma media y CV. El resultado analítico M/G/1 sigue siendo general por segundo momento."
    else:
        n = max(1, min(_i(data, "n", 20), 200))
        sequence = dd1_sequence(t_llegada, t_atencion, n=n)
        waits = [row["Espera (min)"] for row in sequence]
        avg_wait = mean(waits)
        final_wait = waits[-1]
        rho = t_atencion / t_llegada
        result = {
            "modelo": "D/D/1",
            "estable": t_atencion <= t_llegada,
            "lambda": 60.0 / t_llegada,
            "mu": 60.0 / t_atencion,
            "s": 1,
            "rho": rho,
            "L": 0.0,
            "Lq": 0.0,
            "W": (avg_wait + t_atencion) / 60.0,
            "Wq": avg_wait / 60.0,
            "P_espera": sum(w > 0 for w in waits) / len(waits),
            "P_bloqueo": 0.0,
            "lambda_efectiva": 60.0 / t_llegada,
        }
        interpretation = interpret_dd1(t_llegada, t_atencion, avg_wait, final_wait)
        sim_args = None

    if run_simulation and sim_args is not None:
        simulation = simulate_queue(
            t_llegada,
            t_atencion,
            horizon_min=horizon,
            replications=replications,
            **sim_args,
        )

    return {
        "key": key,
        "meta": MODEL_CATALOG[key],
        "analytic": _pack_result(result),
        "interpretation": interpretation,
        "simulation": simulation,
        "sequence": sequence,
        "note": note,
    }


def compare_scenarios(data):
    a = calculate_model(data.get("a", {}), run_simulation=False)
    b = calculate_model(data.get("b", {}), run_simulation=False)
    meta_wq = _f(data, "meta_wq", 10)
    meta_block = max(0.0, min(1.0, _f(data, "meta_block", 0.05)))
    for item in (a, b):
        m = item["analytic"]
        m["meets_wq"] = m["wq_min"] is not None and m["wq_min"] <= meta_wq
        m["meets_block"] = (m["p_block"] or 0.0) <= meta_block
    return {"a": a, "b": b, "meta_wq": meta_wq, "meta_block": meta_block}


def economic_analysis(data):
    t_llegada = _f(data, "t_llegada", 8)
    t_atencion = _f(data, "t_atencion", 12)
    max_servers = max(1, min(_i(data, "max_servers", 12), 50))
    cost_staff = max(0.0, _f(data, "cost_staff", 25))
    cost_wait = max(0.0, _f(data, "cost_wait", 15))
    meta_wq = max(0.0, _f(data, "meta_wq", 10))
    rows = evaluate_mms_capacity(t_llegada, t_atencion, max_servers, cost_staff, cost_wait, meta_wq_min=meta_wq)
    feasible = [r for r in rows if r["meets_service"] and math.isfinite(r["cost_total"])]
    stable = [r for r in rows if r["stable"] and math.isfinite(r["cost_total"])]
    recommended = min(feasible or stable, key=lambda r: (r["cost_total"], r["servers"])) if (feasible or stable) else rows[-1]
    reading = interpret_economic(recommended["cost_staff"], recommended["cost_wait"], recommended["cost_total"], recommended["servers"], recommended["Wq_min"])
    return {"rows": rows, "recommended": recommended, "interpretation": reading}


def sizing_analysis(data):
    t_llegada = _f(data, "t_llegada", 8)
    t_atencion = _f(data, "t_atencion", 12)
    max_servers = max(1, min(_i(data, "max_servers", 20), 60))
    meta_wq = max(0.0, _f(data, "meta_wq", 10))
    meta_p = max(0.0, min(1.0, _f(data, "meta_p_wait", 0.8)))
    sla_t = max(0.0, _f(data, "sla_threshold", 10))
    sla_target = max(0.0, min(1.0, _f(data, "sla_target", 0.9)))
    rows = evaluate_mms_capacity(t_llegada, t_atencion, max_servers, meta_wq_min=meta_wq, meta_p_espera=meta_p)
    for row in rows:
        r = mms_from_minutes(t_llegada, t_atencion, row["servers"])
        service_level = 1.0 - probability_wait_over(r, sla_t)
        row["service_level"] = service_level
        row["meets_sla"] = r["estable"] and service_level >= sla_target
        row["meets_all"] = row["meets_service"] and row["meets_sla"]
    candidates = [r for r in rows if r["meets_all"]]
    recommended = min(candidates, key=lambda r: r["servers"]) if candidates else None
    return {"rows": rows, "recommended": recommended, "sla_threshold": sla_t, "sla_target": sla_target}


def end_to_end_analysis(data):
    t_llegada = _f(data, "t_llegada", 8)
    t_atencion = _f(data, "t_atencion", 12)
    current = max(1, _i(data, "current_servers", 2))
    max_servers = max(current, min(_i(data, "max_servers", 12), 50))
    cost_staff = max(0.0, _f(data, "cost_staff", 25))
    cost_wait = max(0.0, _f(data, "cost_wait", 15))
    meta_wq = max(0.0, _f(data, "meta_wq", 10))
    meta_p = max(0.0, min(1.0, _f(data, "meta_p_wait", 0.8)))

    actual_result = mms_from_minutes(t_llegada, t_atencion, current)
    actual_cost = economic_cost(actual_result, current, cost_staff, cost_wait)
    actual = _pack_result(actual_result)
    actual["cost"] = actual_cost
    rows = evaluate_mms_capacity(t_llegada, t_atencion, max_servers, cost_staff, cost_wait, meta_wq_min=meta_wq, meta_p_espera=meta_p)
    candidates = [r for r in rows if r["meets_service"] and math.isfinite(r["cost_total"])]
    stable = [r for r in rows if r["stable"] and math.isfinite(r["cost_total"])]
    recommended = min(candidates or stable, key=lambda r: (r["cost_total"], r["servers"])) if (candidates or stable) else rows[-1]
    return {
        "actual": actual,
        "actual_interpretation": interpret_mms(actual_result, current),
        "rows": rows,
        "recommended": recommended,
        "recommended_interpretation": interpret_mms(mms_from_minutes(t_llegada, t_atencion, recommended["servers"]), recommended["servers"]),
        "economic_interpretation": interpret_economic(recommended["cost_staff"], recommended["cost_wait"], recommended["cost_total"], recommended["servers"], recommended["Wq_min"]),
        "marginal": marginal_mms_analysis(t_llegada, t_atencion, current),
    }


def _stats(values):
    n = len(values)
    avg = mean(values)
    sd = stdev(values) if n > 1 else 0.0
    cv = sd / avg if avg else 0.0
    lag1 = 0.0
    if n > 2:
        x = values[:-1]
        y = values[1:]
        mx, my = mean(x), mean(y)
        num = sum((a - mx) * (b - my) for a, b in zip(x, y))
        denx = sum((a - mx) ** 2 for a in x)
        deny = sum((b - my) ** 2 for b in y)
        lag1 = num / math.sqrt(denx * deny) if denx > 0 and deny > 0 else 0.0
    return {"n": n, "mean": avg, "sd": sd, "cv": cv, "lag1": lag1, "min": min(values), "max": max(values)}


def validate_csv(uploaded, arrival_column="", service_column=""):
    raw = uploaded.read()
    text = raw.decode("utf-8-sig")
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    headers = reader.fieldnames or []
    rows = list(reader)
    if not headers or not rows:
        raise ValueError("El CSV no contiene datos utilizables.")

    def numeric_values(column):
        vals = []
        for row in rows:
            try:
                v = float(str(row.get(column, "")).replace(",", "."))
                if v > 0 and math.isfinite(v):
                    vals.append(v)
            except (TypeError, ValueError):
                pass
        return vals

    numeric = {h: numeric_values(h) for h in headers}
    candidates = [h for h, vals in numeric.items() if len(vals) >= 2]
    if len(candidates) < 2:
        raise ValueError("Se requieren al menos dos columnas numéricas positivas.")
    arrival_column = arrival_column if arrival_column in candidates else candidates[0]
    service_column = service_column if service_column in candidates and service_column != arrival_column else next(h for h in candidates if h != arrival_column)
    arrivals = numeric[arrival_column]
    services = numeric[service_column]
    a = _stats(arrivals)
    s = _stats(services)

    messages = []
    if 0.8 <= a["cv"] <= 1.2 and abs(a["lag1"]) < 0.2:
        messages.append("Los interarribos son descriptivamente compatibles con una aproximación exponencial/Poisson, pero esto no constituye una prueba formal.")
    else:
        messages.append("Los interarribos muestran desviaciones respecto al patrón exponencial ideal; conviene segmentar por franja o usar simulación.")
    if 0.8 <= s["cv"] <= 1.2:
        messages.append("La variabilidad del servicio es cercana a CV=1; M/M/s puede ser una aproximación inicial si los demás supuestos se sostienen.")
    else:
        messages.append("La variabilidad del servicio difiere de la exponencial; M/G/1 o simulación pueden representar mejor el proceso.")

    return {
        "headers": headers,
        "arrival_column": arrival_column,
        "service_column": service_column,
        "arrival": a,
        "service": s,
        "messages": messages,
        "arrival_values": arrivals[:2000],
        "service_values": services[:2000],
    }
