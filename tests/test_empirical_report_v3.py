import io
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).parents[1] / "django_app"))
from portal.empirical_v3 import import_workbook
from portal.queue_v3 import evaluate
from report_v3 import report_pdf, report_xlsx


CFG={"VERSION_ESQUEMA":"1.0.0","SUCURSAL_ID":"BANCO_001",
     "NIVEL_REGISTRO":"BASICO","MODO_ANALISIS":"SIMULACION_EMPIRICA",
     "INICIO_OBSERVACION":datetime(2026,10,20,8,0),
     "FIN_OBSERVACION":datetime(2026,10,20,18,0),
     "CAPTURA_NO_ATENDIDOS":"SI"}
BASIC=["registro_id","sucursal_id","llegada_ts","estado","servicio_seg",
       "tipo_servicio","prioridad","fuente","observaciones"]
FULL=["registro_id","sucursal_id","cliente_anon","llegada_ts","estado",
      "inicio_atencion_ts","fin_atencion_ts","salida_sin_atencion_ts","ventanilla_id",
      "tipo_servicio","prioridad","motivo_no_atencion","fuente","observaciones"]


def _workbook(config=None,basic=None,full=None):
    c={**CFG,**(config or {})}
    if basic is None:
        basic=[]
        for i in range(5):
            basic.append(dict(registro_id=f"C{i:03d}",sucursal_id="BANCO_001",
                              llegada_ts=datetime(2026,10,20,9,0)+timedelta(minutes=3*i),
                              estado="ATENDIDO",servicio_seg=360,
                              tipo_servicio="GENERAL",prioridad="NORMAL",fuente="SISTEMA"))
    stream=io.BytesIO()
    with pd.ExcelWriter(stream,engine="xlsxwriter") as writer:
        pd.DataFrame(list(c.items()),columns=["CÓDIGO","VALOR / EDITAR"]).to_excel(
            writer,sheet_name="01_Configuracion",index=False,startrow=4)
        pd.DataFrame(basic,columns=BASIC).to_excel(
            writer,sheet_name="02_Registro_Basico",index=False,startrow=5)
        pd.DataFrame(full or [],columns=FULL).to_excel(
            writer,sheet_name="03_Registro_Completo",index=False,startrow=5)
    return stream.getvalue()


def test_basic_workbook_import_and_replicas():
    d=import_workbook(_workbook())
    assert d["valid"],d["errors"]
    assert d["level"]=="BASICO"
    assert len(d["arrival_samples"])==4
    assert set(d["service_samples"])=={6.}
    result=evaluate({"model":"G/G/c","mode":"empirical","horizon":90,"servers":2,
                     "arrival_samples":d["arrival_samples"],"service_samples":d["service_samples"],
                     "replications":3})
    assert result["mode"]=="empirical" and len(result["runs"])==3


def test_both_capture_sheets_rejected():
    bad=[dict(registro_id="X2",sucursal_id="BANCO_001",
              llegada_ts=datetime(2026,10,20,9,0),estado="ATENDIDO",servicio_seg=180)]
    with pytest.raises(ValueError,match="No mezclar"):
        import_workbook(_workbook(full=[{"registro_id":"Y1"}]))


def test_full_workbook_wait_and_chronology():
    r=[]
    for i in range(4):
        t=datetime(2026,10,20,9,0)+timedelta(minutes=8*i)
        r.append(dict(registro_id=str(i),sucursal_id="BANCO_001",cliente_anon=str(i),
                      llegada_ts=t,estado="ATENDIDO",
                      inicio_atencion_ts=t+timedelta(minutes=2),
                      fin_atencion_ts=t+timedelta(minutes=7),
                      ventanilla_id="V01"))
    d=import_workbook(_workbook(config={"NIVEL_REGISTRO":"COMPLETO"},basic=[],full=r))
    assert d["valid"],d["errors"]
    assert d["avg_interarrival"]==8.
    assert d["avg_service"]==5.


def test_duplicate_and_inverted_service_rejected():
    rows=[dict(registro_id="C01",sucursal_id="BANCO_001",
               llegada_ts=datetime(2026,10,20,9,0)+timedelta(minutes=3*i),
               estado="ATENDIDO",servicio_seg=360) for i in range(4)]
    d=import_workbook(_workbook(basic=rows))
    assert not d["valid"]
    assert any("duplicado" in e for e in d["errors"])


def test_report_formats_consistent():
    result=evaluate({"model":"D/D/c","mode":"deterministic","horizon":120,
                     "arrival_mean":5,"service_mean":8,"servers":3})
    pdf=report_pdf(result)
    xlsx=report_xlsx(result)
    assert pdf.startswith(b"%PDF")
    assert xlsx.startswith(b"PK")
    xls=pd.ExcelFile(io.BytesIO(xlsx))
    assert {"Ficha","Resultados","Replicas","Eventos","Evolucion","IC_95"}.issubset(xls.sheet_names)
