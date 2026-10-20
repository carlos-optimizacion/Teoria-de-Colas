import csv, io, json
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .challenge_engine import SCENARIOS
from .models import GameRun, SavedScenario, UserProgress

def signup(request):
    if request.user.is_authenticated:return redirect("portal:aplicativo_app")
    form=UserCreationForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        user=form.save(); UserProgress.objects.get_or_create(user=user); login(request,user)
        return redirect("portal:aplicativo_app")
    return render(request,"registration/signup.html",{"form":form})

@login_required
def progress(request):
    p,_=UserProgress.objects.get_or_create(user=request.user)
    runs=request.user.queue_runs.all()[:20]
    best={key:request.user.queue_runs.filter(scenario=key).order_by("-score").first() for key in SCENARIOS}
    return render(request,"portal/progress.html",{"active":"progress","progress":p,"runs":runs,"best":best,"scenarios":SCENARIOS})

def leaderboard(request):
    scenario=request.GET.get("scenario","")
    qs=GameRun.objects.filter(user__isnull=False)
    if scenario in SCENARIOS:qs=qs.filter(scenario=scenario)
    # one best run per user, deterministic display after sorting in Python
    best={}
    for run in qs.select_related("user").order_by("-score","created_at")[:1000]:
        best.setdefault(run.user_id,run)
    rows=sorted(best.values(),key=lambda r:(-float(r.score),r.created_at))[:50]
    return render(request,"portal/leaderboard.html",{"active":"leaderboard","rows":rows,"scenarios":SCENARIOS,"selected":scenario})

@login_required
def reports(request):
    runs=request.user.queue_runs.all()[:100]
    return render(request,"portal/reports.html",{"active":"reports","runs":runs})

@login_required
def run_report(request,run_id):
    run=get_object_or_404(GameRun,user=request.user,id=run_id)
    return render(request,"portal/run_report.html",{"active":"reports","run":run})

@login_required
def run_export(request,run_id,fmt):
    run=get_object_or_404(GameRun,user=request.user,id=run_id)
    payload={"id":run.id,"scenario":run.scenario,"title":run.title,"score":float(run.score),"passed":run.passed,
             "metrics":run.metrics,"staffing":run.staffing,"actions":run.actions,"config":run.config,
             "created_at":run.created_at.isoformat()}
    if fmt=="json":
        response=JsonResponse(payload,json_dumps_params={"indent":2}); response["Content-Disposition"]=f'attachment; filename="decision-lab-run-{run.id}.json"'; return response
    if fmt=="csv":
        response=HttpResponse(content_type="text/csv");response["Content-Disposition"]=f'attachment; filename="decision-lab-run-{run.id}.csv"'
        w=csv.writer(response);w.writerow(["campo","valor"])
        for k,v in payload.items():w.writerow([k,json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v])
        return response
    if fmt=="pdf":
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError as exc: raise Http404("PDF no disponible") from exc
        response=HttpResponse(content_type="application/pdf");response["Content-Disposition"]=f'attachment; filename="decision-lab-run-{run.id}.pdf"'
        c=canvas.Canvas(response,pagesize=A4);w,h=A4;y=h-52
        c.setFont("Helvetica-Bold",16);c.drawString(48,y,"Decision Lab 2.0 — Reporte de simulación");y-=26
        c.setFont("Helvetica",10)
        rows=[("Escenario",run.title),("Fecha",run.created_at.strftime("%Y-%m-%d %H:%M")),("Puntuación",str(run.score)),("Meta cumplida","Sí" if run.passed else "No"),
              ("Réplicas",str(run.replications)),("Semilla",str(run.seed))]
        for k,v in rows:c.drawString(48,y,f"{k}: {v}");y-=16
        y-=8;c.setFont("Helvetica-Bold",11);c.drawString(48,y,"Indicadores");y-=18;c.setFont("Helvetica",9)
        for k,v in run.metrics.items():
            c.drawString(58,y,f"{k}: {v}");y-=14
            if y<60:c.showPage();y=h-52;c.setFont("Helvetica",9)
        c.save();return response
    raise Http404("Formato no soportado")

@login_required
@require_POST
def save_scenario(request):
    try:
        data=json.loads(request.body or "{}");name=str(data.get("name") or "Escenario guardado")[:100];scenario=data.get("scenario")
        if scenario not in SCENARIOS:raise ValueError("Escenario inválido")
        item=SavedScenario.objects.create(user=request.user,name=name,scenario=scenario,payload=data.get("payload") or {})
        return JsonResponse({"ok":True,"id":item.id,"name":item.name})
    except (ValueError,TypeError,json.JSONDecodeError) as exc:return JsonResponse({"ok":False,"error":str(exc)},status=400)
