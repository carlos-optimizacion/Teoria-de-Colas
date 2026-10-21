"""XLSX audit-friendly comparison of already evaluated simulation snapshots."""
from __future__ import annotations

import io
import json
import xlsxwriter

from experiment_registry_v3 import comparison_rows, recommend_comparison


def comparison_xlsx(items: list[dict]) -> bytes:
    if not items:
        raise ValueError("No hay corridas que exportar")
    rows=comparison_rows(items)
    verdict=recommend_comparison(items) if len(items)>=2 else {
        "valid":False,"reason":"Se requiere una segunda corrida","recommended":None,
        "target":None,"cost":None,"sla":None,
    }
    out=io.BytesIO()
    workbook=xlsxwriter.Workbook(out,{"in_memory":True})
    dark=workbook.add_format({"bold":True,"font_color":"white","bg_color":"#173A57",
                              "border":1,"text_wrap":True,"valign":"vcenter"})
    title=workbook.add_format({"bold":True,"font_size":16,"font_color":"#173A57"})
    num=workbook.add_format({"num_format":"#,##0.00"})
    integer=workbook.add_format({"num_format":"#,##0"})
    normal=workbook.add_format({"text_wrap":True,"valign":"top"})
    note=workbook.add_format({"italic":True,"font_color":"#656C75","text_wrap":True})
    def put(sheet,row,col,value,fmt=None):
        if isinstance(value,bool):
            sheet.write_boolean(row,col,value,fmt)
        elif isinstance(value,(int,float)):
            sheet.write_number(row,col,value,fmt or num)
        elif value is None:
            sheet.write_blank(row,col,None,fmt)
        else:
            txt=str(value)
            if txt.startswith(("=","+","-","@")): txt="'"+txt
            sheet.write_string(row,col,txt,fmt or normal)
    sh=workbook.add_worksheet("Comparacion")
    sh.freeze_panes(4,1)
    sh.set_column(0,0,21)
    sh.set_column(1,3,19)
    sh.set_column(4,13,20)
    sh.set_row(3,35)
    sh.write_string(0,0,"ASTALANKA OPT · COMPARACIÓN DE CORRIDAS",title)
    sh.write_string(1,0,verdict["reason"],note)
    headers=list(rows[0])
    for i,name in enumerate(headers):sh.write_string(3,i,name,dark)
    for ri,row in enumerate(rows,4):
        for ci,name in enumerate(headers):
            put(sh,ri,ci,row[name],integer if name in {"Réplicas","Servidores","Rechazados","Horizonte (min)"} else None)
    sh.autofilter(3,0,3+len(rows),len(headers)-1)
    sh.write_string(6+len(rows),0,"Recomendación",dark)
    sh.write_string(6+len(rows),1,str(verdict.get("recommended") or "No disponible"),normal)
    sh.write_string(7+len(rows),0,"Nota",dark)
    sh.merge_range(7+len(rows),1,7+len(rows),8,
        "Menor costo observado únicamente entre corridas comparables que satisfacen el SLA. "
        "No demuestra óptimo global ni significancia estadística.",note)
    meta=workbook.add_worksheet("Supuestos")
    meta.set_column(0,0,22);meta.set_column(1,1,19);meta.set_column(2,2,42)
    meta.write_row(0,0,["ID","Parámetro","Valor"],dark)
    rr=1
    for snap in items:
        for key,value in sorted(snap.get("parameters",{}).items()):
            put(meta,rr,0,snap["id"])
            put(meta,rr,1,key)
            put(meta,rr,2,json.dumps(value,ensure_ascii=False,sort_keys=True)
                if isinstance(value,(dict,list)) else value)
            rr+=1
    sources=workbook.add_worksheet("Trazabilidad")
    sources.set_column(0,0,20);sources.set_column(1,1,23)
    sources.set_column(2,3,53)
    sources.write_row(0,0,["ID","Motor","Método","Semilla / Réplicas"],dark)
    for ri,item in enumerate(items,1):
        for ci,value in enumerate([item["id"],item.get("source",""),
                item.get("method",""),
                f"{item.get('seed')} / {item.get('replications')}"]):
            put(sources,ri,ci,value)
    sources.write_string(len(items)+3,0,
        "Las fuentes históricas, cuando existen, se identifican por hash. "
        "Las observaciones individuales no se almacenan aquí.",note)
    workbook.close()
    return out.getvalue()
