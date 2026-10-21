"""Puente entre fórmulas analíticas estacionarias y simulación transitoria v3."""
from __future__ import annotations
from math import sqrt
from queue_core import mms_from_minutes, mmsk_from_minutes, mg1_from_minutes


def _cv_service(spec):
    if spec.service_dist == "deterministic":
        return 0.
    if spec.service_dist == "exponential":
        return 1.
    if spec.service_dist in ("gamma", "lognormal"):
        return spec.service_cv
    if spec.service_dist == "triangular":
        return sqrt(3/32)
    return None


def analytic(spec):
    """Nunca presenta una fórmula exacta para un caso que no cumple sus supuestos.

    Medias W y Wq se devuelven en minutos a diferencia de queue_core
    (horas); L/Lq/P/rho conservan sus unidades.
    """
    if len(set(spec.staffing))>1:
        return {"available":False,"reason":"La dotación varía por franja; no corresponde usar fórmulas estacionarias de capacidad constante."}
    if spec.mode == "empirical":
        return {"available":False,"reason":"Las distribuciones empíricas no han sido certificadas como Markovianas; se reporta DES."}
    result = None
    if spec.model in ("M/M/1","M/M/c"):
        result=mms_from_minutes(spec.arrival_mean,spec.service_mean,spec.servers)
    elif spec.model in ("M/M/1/K","M/M/c/K","M/M/c/c (Erlang B)"):
        result=mmsk_from_minutes(spec.arrival_mean,spec.service_mean,spec.servers,spec.capacity)
    elif spec.model=="M/G/1":
        cv=_cv_service(spec)
        if cv is not None:
            result=mg1_from_minutes(spec.arrival_mean,spec.service_mean,cv)
    if result is None:
        return {"available":False,"reason":"No se dispone de fórmula estacionaria exacta para esta configuración."}
    keys=("L","Lq","W","Wq","rho","P_espera","P_bloqueo","estable","lambda","mu")
    output={k:result[k] for k in keys if k in result}
    for k in ("W","Wq"):
        if k in output:
            output[k] *= 60.
    return {"available":True,"metrics":output,
            "condition":"Teoría estacionaria: demanda y servicios homogéneos con supuestos Kendall. "
                        "No es una predicción exacta de una jornada inicialmente vacía y finita.",
            "units":{"W":"min","Wq":"min","L":"clientes","Lq":"clientes","lambda":"clientes/h"}}
