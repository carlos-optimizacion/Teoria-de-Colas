"""Gamified operations views backed by the real finite-horizon simulator."""
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .challenge_engine import SCENARIOS, evaluate_game
from .models import GameRun, UserProgress

def _leaderboard(limit=5):
    best={}
    for run in GameRun.objects.filter(user__isnull=False).select_related("user").order_by("-score","created_at")[:500]:
        best.setdefault(run.user_id,run)
    return sorted(best.values(),key=lambda r:(-float(r.score),r.created_at))[:limit]

@ensure_csrf_cookie
def challenge(request):
    progress=None
    if request.user.is_authenticated:
        progress,_=UserProgress.objects.get_or_create(user=request.user)
    return render(request,"portal/challenge.html",{
        "active":"challenge","scenarios":SCENARIOS,"progress":progress,"leaders":_leaderboard(),
    })

@require_POST
def challenge_api(request):
    try:
        body=json.loads(request.body or "{}")
        result=evaluate_game(body)
        if not request.session.session_key:
            request.session.create()
        user=request.user if request.user.is_authenticated else None
        previous=None
        if user:
            previous=GameRun.objects.filter(user=user,scenario=result["scenario"]).order_by("-score").first()
        run=GameRun.objects.create(
            user=user,session_key=request.session.session_key or "",scenario=result["scenario"],title=result["title"],
            score=result["score"],passed=result["passes"]["budget"] and result["passes"]["sla"],
            seed=int(body.get("seed",2026)),replications=result["replications"],staffing=result["staffing"],actions=result["actions"],
            metrics=result["metrics"],config=result["config"],
        )
        progress_data=None
        if user:
            progress,_=UserProgress.objects.get_or_create(user=user)
            old_best=float(previous.score) if previous else -1
            new_best=float(result["score"])>old_best
            first_pass=run.passed and not GameRun.objects.filter(user=user,scenario=result["scenario"],passed=True).exclude(pk=run.pk).exists()
            xp=5
            coins=2
            achievement=None
            if first_pass:
                xp=100;coins=100;achievement="Dominio: "+result["title"]
            elif new_best:
                xp=25+max(0,int(float(result["score"])-max(old_best,0)));coins=20
            progress.award(xp=xp,coins=coins,scenario=result["scenario"] if run.passed else None,achievement=achievement)
            progress_data={"level":progress.level,"xp":progress.xp,"coins":progress.coins,"achievements":progress.achievements}
        return JsonResponse({"ok":True,**result,"run_id":run.id,"progress":progress_data},json_dumps_params={"allow_nan":False})
    except (ValueError,TypeError,OverflowError,json.JSONDecodeError) as exc:
        return JsonResponse({"ok":False,"error":str(exc)},status=400)
