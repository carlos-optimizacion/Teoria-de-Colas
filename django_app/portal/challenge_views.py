"""Vistas aisladas de gamificación, sin cambiar el portal existente."""
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .challenge_engine import SCENARIOS, evaluate_game

@ensure_csrf_cookie
def challenge(request):
    return render(request, "portal/challenge.html", {"active":"challenge","scenarios":SCENARIOS})

@require_POST
def challenge_api(request):
    try:
        body=json.loads(request.body or "{}")
        return JsonResponse({"ok":True,**evaluate_game(body)},json_dumps_params={"allow_nan":False})
    except (ValueError,TypeError,OverflowError,json.JSONDecodeError) as exc:
        return JsonResponse({"ok":False,"error":str(exc)},status=400)
