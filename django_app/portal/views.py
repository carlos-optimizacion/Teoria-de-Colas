import json
import math

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .services import (
    CASES,
    MODEL_CATALOG,
    calculate_model,
    compare_scenarios,
    economic_analysis,
    end_to_end_analysis,
    sizing_analysis,
    validate_csv,
)
from .visual_service import visual_end_to_end_payload


def _json_body(request):
    return json.loads(request.body or "{}")


def _json_safe(value):
    """Convierte resultados Python a JSON estricto compatible con navegadores.

    Los modelos de colas usan infinito para representar métricas sin estado
    estacionario en escenarios inestables. JSON no admite Infinity ni NaN, por
    lo que esos valores se exponen como null sin alterar el cálculo interno.
    """
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _json_response(payload, status=200):
    return JsonResponse(
        _json_safe(payload),
        status=status,
        json_dumps_params={"allow_nan": False},
    )


def _error(exc):
    return _json_response({"ok": False, "error": str(exc)}, status=400)


@ensure_csrf_cookie
def home(request):
    return render(request, "portal/home.html", {"active": "home", "models": MODEL_CATALOG})


@ensure_csrf_cookie
def fundamentals(request):
    return render(request, "portal/fundamentals.html", {"active": "fundamentals"})


def _model_page(request, key, active=None, title=None, subtitle=None):
    config = dict(MODEL_CATALOG[key])
    if title:
        config["name"] = title
    if subtitle:
        config["subtitle"] = subtitle
    initial = {
        "t_llegada": request.GET.get("t_llegada", "10"),
        "t_atencion": request.GET.get("t_atencion", "8"),
        "servers": request.GET.get("servers", "2"),
        "capacity": request.GET.get("capacity", "8"),
        "waiting_places": request.GET.get("waiting_places", "5"),
        "cv": request.GET.get("cv", "1.0"),
        "n": request.GET.get("n", "20"),
    }
    return render(request, "portal/model.html", {"active": active or key, "model_key": key, "config": config, "initial": initial})


@ensure_csrf_cookie
def model_mm1(request): return _model_page(request, "mm1")
@ensure_csrf_cookie
def model_mms(request): return _model_page(request, "mms")
@ensure_csrf_cookie
def model_mmsk(request): return _model_page(request, "mmsk")
@ensure_csrf_cookie
def model_mm1c(request): return _model_page(request, "mm1c", title="M/M/1/c")
@ensure_csrf_cookie
def model_mmstotal(request): return _model_page(request, "mmstotal", title="M/M/s/c")
@ensure_csrf_cookie
def model_erlangb(request): return _model_page(request, "erlangb", title="M/M/c/c · Erlang B")
@ensure_csrf_cookie
def model_mg1(request): return _model_page(request, "mg1")
@ensure_csrf_cookie
def model_dd1(request): return _model_page(request, "dd1")


@ensure_csrf_cookie
def cases(request):
    return render(request, "portal/cases.html", {"active": "cases", "cases": CASES})


@ensure_csrf_cookie
def simple_lab(request):
    return _model_page(request, "mms", active="simple", title="Laboratorio de colas simples", subtitle="Explora M/M/1 y M/M/s variando el número de servidores.")


@ensure_csrf_cookie
def complex_lab(request):
    return _model_page(request, "mmsk", active="complex", title="Laboratorio de colas complejas", subtitle="Explora capacidad finita, bloqueo y tasa efectiva admitida.")


@ensure_csrf_cookie
def comparator(request):
    return render(request, "portal/tool.html", {"active": "comparator", "tool_key": "comparator", "title": "Comparador de modelos"})


@ensure_csrf_cookie
def economics(request):
    return render(request, "portal/tool.html", {"active": "economics", "tool_key": "economics", "title": "Análisis económico"})


@ensure_csrf_cookie
def sizing(request):
    return render(request, "portal/tool.html", {"active": "sizing", "tool_key": "sizing", "title": "Dimensionamiento de servidores"})


@ensure_csrf_cookie
def validator(request):
    return render(request, "portal/validator.html", {"active": "validator"})


@ensure_csrf_cookie
def end_to_end(request):
    return render(request, "portal/tool.html", {"active": "endtoend", "tool_key": "endtoend", "title": "Análisis End-to-End"})


@require_POST
def model_api(request):
    try:
        return _json_response({"ok": True, **calculate_model(_json_body(request))})
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        return _error(exc)


@require_POST
def compare_api(request):
    try:
        return _json_response({"ok": True, **compare_scenarios(_json_body(request))})
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        return _error(exc)


@require_POST
def economic_api(request):
    try:
        return _json_response({"ok": True, **economic_analysis(_json_body(request))})
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        return _error(exc)


@require_POST
def sizing_api(request):
    try:
        return _json_response({"ok": True, **sizing_analysis(_json_body(request))})
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        return _error(exc)


@require_POST
def validator_api(request):
    try:
        uploaded = request.FILES.get("file")
        if not uploaded:
            raise ValueError("Selecciona un archivo CSV.")
        result = validate_csv(uploaded, request.POST.get("arrival_column", ""), request.POST.get("service_column", ""))
        return _json_response({"ok": True, **result})
    except (TypeError, ValueError, UnicodeDecodeError) as exc:
        return _error(exc)


@require_POST
def end_to_end_api(request):
    try:
        data = _json_body(request)
        analysis = end_to_end_analysis(data)
        analysis["visual"] = visual_end_to_end_payload(data, analysis)
        return _json_response({"ok": True, **analysis})
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        return _error(exc)


# Alias compatible con la primera fase del PR.
queue_api = model_api
