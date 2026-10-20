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
from .simulator_service import simulator_analysis
from .challenge_engine import SCENARIOS
from .models import UserProgress


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
    return render(request, "portal/challenge.html", {"active": "challenge", "scenarios": SCENARIOS})


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


@ensure_csrf_cookie
def simulator(request):
    return render(request, "portal/simulator.html", {"active": "simulator"})


@require_POST
def model_api(request):
    try:
        body=_json_body(request)
        result=calculate_model(body)
        progress_data=None
        if request.user.is_authenticated:
            key=str(body.get("model",""))
            progress,_=UserProgress.objects.get_or_create(user=request.user)
            models=list(progress.completed_models or [])
            if key in MODEL_CATALOG and key not in models:
                models.append(key);progress.completed_models=models;progress.xp+=30;progress.coins+=15
                progress.level=UserProgress.level_for_xp(progress.xp)
                achievements=list(progress.achievements or [])
                if len(models)>=len(MODEL_CATALOG) and "Dominio de los 8 modelos" not in achievements:
                    achievements.append("Dominio de los 8 modelos");progress.achievements=achievements
                progress.save()
            progress_data={"level":progress.level,"xp":progress.xp,"coins":progress.coins,"completed_models":len(progress.completed_models or [])}
        return _json_response({"ok": True, **result,"progress":progress_data})
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
        return _json_response({"ok": True, **end_to_end_analysis(_json_body(request))})
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        return _error(exc)


@require_POST
def simulator_api(request):
    try:
        return _json_response({"ok": True, **simulator_analysis(_json_body(request))})
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        return _error(exc)


# Alias compatible con la primera fase del PR.
queue_api = model_api


@ensure_csrf_cookie
def exercises(request):
    items=[
        {"title":"Banco: dimensionar ventanillas","model":"M/M/s","prompt":"Compara 2, 3 y 4 servidores y justifica el menor costo que cumpla el SLA.","url":"portal:mms"},
        {"title":"Supermercado: capacidad limitada","model":"M/M/s/K","prompt":"Evalúa bloqueo y tasa efectiva cuando el sistema tiene aforo limitado.","url":"portal:mmsk"},
        {"title":"Call center: pérdida sin espera","model":"Erlang B","prompt":"Calcula probabilidad de bloqueo sin sala de espera.","url":"portal:erlangb"},
        {"title":"Servicio variable","model":"M/G/1","prompt":"Analiza el efecto del coeficiente de variación sobre Wq.","url":"portal:mg1"},
        {"title":"Proceso determinista","model":"D/D/1","prompt":"Construye la secuencia de llegada, inicio, salida y espera.","url":"portal:dd1"},
    ]
    return render(request,"portal/exercises.html",{"active":"exercises","items":items})

@ensure_csrf_cookie
def glossary(request):
    terms=[
        ("λ (lambda)","Tasa promedio de llegadas por unidad de tiempo."),
        ("μ (mu)","Tasa promedio de servicio de un servidor."),
        ("ρ (rho)","Utilización de la capacidad; en M/M/s, λ/(sμ)."),
        ("Lq","Número promedio de clientes en cola."),
        ("L","Número promedio de clientes en el sistema."),
        ("Wq","Tiempo promedio de espera antes de iniciar servicio."),
        ("W","Tiempo promedio total en el sistema."),
        ("SLA","Meta probabilística o temporal de nivel de servicio."),
        ("Bloqueo","Cliente que no ingresa por falta de capacidad."),
        ("Abandono","Cliente admitido que se retira antes de ser atendido."),
        ("Erlang C","Modelo de espera para M/M/s con capacidad de cola ilimitada."),
        ("Erlang B","Modelo de pérdidas sin cola de espera."),
        ("Ley de Little","Relación L=λW, bajo condiciones de estabilidad pertinentes."),
    ]
    return render(request,"portal/glossary.html",{"active":"glossary","terms":terms})
