import json
import math

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from interpretation_core import interpret_mm1, interpret_mms
from queue_core import mms_from_minutes
from simulation_core import simulate_mms


def _safe(value):
    return value if isinstance(value, (int, float)) and math.isfinite(value) else None


def _analytic_payload(result):
    return {
        "stable": result["estable"],
        "lambda": result["lambda"],
        "mu": result["mu"],
        "servers": result["s"],
        "rho": result["rho"],
        "p_wait": result["P_espera"],
        "wq_min": _safe(result["Wq"] * 60.0),
        "w_min": _safe(result["W"] * 60.0),
        "lq": _safe(result["Lq"]),
        "l": _safe(result["L"]),
    }


@ensure_csrf_cookie
def home(request):
    return render(request, "portal/home.html", {"active": "home"})


@ensure_csrf_cookie
def model_mm1(request):
    return render(request, "portal/model.html", {
        "active": "mm1", "model_key": "mm1", "model_name": "M/M/1",
        "subtitle": "Una cola, un servidor y capacidad de espera ilimitada.",
        "fixed_servers": 1,
    })


@ensure_csrf_cookie
def model_mms(request):
    return render(request, "portal/model.html", {
        "active": "mms", "model_key": "mms", "model_name": "M/M/s",
        "subtitle": "Una cola compartida por múltiples servidores equivalentes.",
        "fixed_servers": None,
    })


@require_POST
def queue_api(request):
    try:
        data = json.loads(request.body or "{}")
        model = data.get("model", "mms")
        t_llegada = float(data.get("t_llegada", 10))
        t_atencion = float(data.get("t_atencion", 8))
        servers = 1 if model == "mm1" else int(data.get("servers", 2))
        horizon = max(60.0, min(float(data.get("horizon", 480)), 1440.0))
        replications = max(1, min(int(data.get("replications", 30)), 200))

        result = mms_from_minutes(t_llegada, t_atencion, servers)
        interpretation = interpret_mm1(result) if servers == 1 else interpret_mms(result, servers)
        simulation = simulate_mms(t_llegada, t_atencion, servers, horizon, replications)
        return JsonResponse({
            "ok": True,
            "model": "M/M/1" if servers == 1 else "M/M/s",
            "analytic": _analytic_payload(result),
            "simulation": simulation,
            "interpretation": interpretation,
        })
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
