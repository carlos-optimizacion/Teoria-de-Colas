"""Reportes reproducibles de Decision Lab 3.0; resultado único del motor."""
from __future__ import annotations
import io
import json
from datetime import datetime, timezone

import pandas as pd


def _clean(value):
    return str(value).replace("—","-").replace("→","->").replace("≥",">=").replace("ρ","rho").replace("λ","lambda")


def report_xlsx(result: dict, optimization: dict | None = None, dynamic: dict | None = None) -> bytes:
    """Exporta parámetros, estadísticas y eventos de la réplica visualizada."""
    stream=io.BytesIO()
    with pd.ExcelWriter(stream,engine="xlsxwriter") as writer:
        meta = {"modelo":result["model"],"modalidad":result["mode"],
                "horizonte_min":result["horizon"],"repeticiones":result["replications_effective"],
                "semilla":result["seed"],"replica_visualizada":result.get("selected_replica",1),
                "servidores":result["servers"],
                "capacidad":result["capacity"],"fecha_exportacion_utc":datetime.now(timezone.utc).isoformat()}
        for name, obj in (
            ("Ficha",pd.DataFrame(meta.items(),columns=["Parámetro","Valor"])),
            ("Resultados",pd.DataFrame(result["metrics"].items(),columns=["Indicador","Media"])),
            ("IC_95",pd.DataFrame.from_dict(result["confidence_95"],orient="index").reset_index(names="Indicador")),
            ("Replicas",pd.DataFrame(result["runs"])),
            ("Evolucion",pd.DataFrame(result["series"])),
        ):
            obj.to_excel(writer,sheet_name=name,index=False)
            sheet=writer.sheets[name]
            sheet.freeze_panes(1,0)
            sheet.set_column(0,0,27)
            sheet.set_column(1,max(1,len(obj.columns)-1),19)
        event_rows=[{k:v for k,v in f.items() if k not in ("queue_ids","servers","priority_ids")} for f in result["events"]]
        pd.DataFrame(event_rows).to_excel(writer,sheet_name="Eventos",index=False)
        writer.sheets["Eventos"].freeze_panes(1,0)
        cfg={}
        for k,v in result["parameters"].items():
            if k in ("arrival_samples","service_samples") and isinstance(v,(list,tuple)):
                cfg[k]=f"{len(v)} observaciones; consultar pestaña Muestras"
            elif isinstance(v,(dict,list)):
                cfg[k]=json.dumps(v,ensure_ascii=False)
            else:
                cfg[k]=v
        pd.DataFrame(cfg.items(),columns=["Campo","Valor"]).to_excel(writer,sheet_name="Configuracion",index=False)
        if "arrival_samples" in result["parameters"] or "service_samples" in result["parameters"]:
            aa=result["parameters"].get("arrival_samples",[])
            bb=result["parameters"].get("service_samples",[])
            n=max(len(aa),len(bb))
            pd.DataFrame({"interarribo_min":list(aa)+[None]*(n-len(aa)),
                          "servicio_min":list(bb)+[None]*(n-len(bb))}).to_excel(
                              writer,sheet_name="MuestrasEmp",index=False)
        writer.sheets["Configuracion"].set_column(0,0,30)
        writer.sheets["Configuracion"].set_column(1,1,60)
        theory=result.get("theory",{})
        if theory.get("available"):
            pd.DataFrame(theory["metrics"].items(),columns=["Indicador","Valor teórico"]).to_excel(writer,sheet_name="Teoria",index=False)
        if dynamic:
            pd.DataFrame([{"bloque":i+1,"inicio_min":i*60,"servidores":c} for i,c in enumerate(dynamic["schedule"])]).to_excel(writer,sheet_name="Turnos_Opt",index=False)
        if optimization:
            pd.DataFrame(optimization["alternatives"]).to_excel(writer,sheet_name="Optimizador",index=False)
            writer.sheets["Optimizador"].freeze_panes(1,0)
            writer.sheets["Optimizador"].set_column(0,10,18)
    return stream.getvalue()


def report_pdf(result: dict, optimization: dict | None = None, dynamic: dict | None = None) -> bytes:
    """Informe técnico-gerencial con análisis temporal y trazabilidad básica."""
    import os
    import tempfile
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from fpdf import FPDF

    pdf=FPDF()
    pdf.set_auto_page_break(auto=True,margin=14)
    pdf.add_page()
    def title(s):
        pdf.set_font("Arial","B",14)
        pdf.set_text_color(22,61,91)
        pdf.cell(0,10,_clean(s),ln=1)
        pdf.set_draw_color(195,216,229)
        pdf.line(10,pdf.get_y(),200,pdf.get_y())
        pdf.ln(4)
    def paragraph(s):
        pdf.set_text_color(48,64,76)
        pdf.set_font("Arial","",9)
        pdf.multi_cell(0,5,_clean(s))
    def row(k,v):
        if pdf.get_y()>265:
            pdf.add_page()
        pdf.set_fill_color(245,248,251)
        pdf.set_font("Arial","",9)
        pdf.cell(84,7,_clean(k)[:43],border=1,fill=True)
        pdf.set_font("Arial","B",9)
        pdf.cell(105,7,_clean(v)[:63],border=1,ln=1)

    title("DECISION LAB 3.0 - Informe de simulacion")
    paragraph("Informe generado a partir del motor de eventos discretos de Python.")
    row("Modelo matematico",result["model"])
    row("Modalidad",result["mode"])
    row("Horizonte",str(result["horizon"])+" min")
    row("Replicas efectivas",result["replications_effective"])
    row("Replica reproducida",result.get("selected_replica",1))
    row("Semilla",result["seed"])
    row("Servidores",result["servers"])
    row("Capacidad total",result["capacity"] if result["capacity"] is not None else "Sin limite")
    title("Indicadores consolidados")
    for k,v in result["metrics"].items():
        row(k,f"{v:,.4f}" if isinstance(v,float) else v)
    paragraph("SLA: fraccion de admitidos que iniciaron servicio antes del umbral; "
              "los pendientes al cierre se incluyen en el denominador. "
              "Costo y tiempos corresponden al horizonte finito configurado.")
    title("Incertidumbre estadistica")
    for k,v in result["confidence_95"].items():
        row(k,("IC 95% ["+str(v["low"])+", "+str(v["high"])+"]")
            if v["low"] is not None else "Sin IC: menos de 2 replicas")
    paragraph("IC exploratorios mediante aproximacion normal sobre medias de replicas. "
              "Con muestras pequenas o indicadores limitados en [0,1], "
              "la cobertura puede diferir del nivel nominal.")
    theory=result.get("theory",{})
    title("Validacion matematica")
    if theory.get("available"):
        paragraph(theory["condition"])
        for k,v in theory["metrics"].items():
            row(k,f"{v:.5f}" if isinstance(v,float) else v)
    else:
        paragraph(theory.get("reason","No existe comparacion teorica exacta"))
    title("Evolucion temporal de la primera replica")
    series=result["series"]
    path=None
    try:
        fig,axs=plt.subplots(2,1,figsize=(7,4.5),sharex=True)
        t=[s["t"] for s in series]
        axs[0].step(t,[s["queue"] for s in series],where="post",label="Cola")
        axs[0].set_ylabel("En cola")
        axs[0].grid(alpha=.25)
        axs[1].step(t,[s["busy"] for s in series],where="post",label="Ventanillas ocupadas")
        axs[1].set_xlabel("Tiempo (min)")
        axs[1].set_ylabel("Ocupadas")
        axs[1].grid(alpha=.25)
        fig.tight_layout()
        fd,path=tempfile.mkstemp(suffix=".png")
        os.close(fd)
        fig.savefig(path,dpi=145)
        plt.close(fig)
        if pdf.get_y()>175:
            pdf.add_page()
        pdf.image(path,x=12,y=pdf.get_y()+2,w=183)
        pdf.ln(122)
    finally:
        if path and os.path.exists(path):
            os.unlink(path)
    if optimization:
        title("Evaluacion automatica de dotacion fija")
        for t in optimization["alternatives"]:
            row(f"{t['servers']} servidores",
                f"SLA {t['sla']*100:.1f}% | Costo S/ {t['total_cost']:,.2f} | "
                +("cumple media" if t["feasible_mean"] else "no cumple"))
        win=optimization["recommended"]
        paragraph("Recomendacion por menor costo con SLA medio: "+
                  (str(win["servers"])+" servidores" if win else "no hay alternativa factible"))
        paragraph(optimization["caveat"])
    if dynamic:
        title("Optimización por turnos (heurística)")
        for i,c in enumerate(dynamic["schedule"]):
            row(f"Bloque {i+1} [{i*60},{min(result['horizon'],(i+1)*60)}) min",f"{c} servidores")
        paragraph(dynamic.get("caveat",dynamic.get("message","")))
    title("Reproducibilidad")
    paragraph("Configuracion original y resultados completos disponibles en el archivo "
              "Excel y el JSON del mismo experimento. "
              "No deben interpretarse como mediciones historicas reales las nuevas "
              "trayectorias estocasticas generadas desde datos empiricos.")
    return pdf.output(dest="S").encode("latin-1")
