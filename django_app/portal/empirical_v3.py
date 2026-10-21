"""Importación estricta de la plantilla oficial Decision Lab 1.0.0.

NO corrige datos silenciosamente. Conservar los bytes originales en la sesión
corresponde a la capa Streamlit. Datos críticos inválidos impiden simular.
"""
from __future__ import annotations
from io import BytesIO
import math

BASIC = ("registro_id","sucursal_id","llegada_ts","estado","servicio_seg",
         "tipo_servicio","prioridad","fuente","observaciones")
FULL = ("registro_id","sucursal_id","cliente_anon","llegada_ts","estado",
        "inicio_atencion_ts","fin_atencion_ts","salida_sin_atencion_ts","ventanilla_id",
        "tipo_servicio","prioridad","motivo_no_atencion","fuente","observaciones")
RECORD_SHEETS = {"BASICO":("02_Registro_Basico", BASIC),
                 "COMPLETO":("03_Registro_Completo",FULL)}
VALID_STATES = {"ATENDIDO","ABANDONO","RECHAZO","DESCONOCIDO","ESPERA_AL_CORTE","SERVICIO_AL_CORTE"}


def import_workbook(data: bytes) -> dict:
    """Extraer interarribos/servicios validables y reporte de calidad.

    Importa el esquema exacto. Requiere fechas Excel completas; no incluye
    filas vacías ni columnas de cálculo del usuario como datos de entrada.
    """
    import pandas as pd
    if not isinstance(data,(bytes,bytearray)) or len(data)>12_000_000:
        raise ValueError("Archivo vacío o mayor a 12 MB")
    if not data[:2]==b"PK":
        raise ValueError("Se requiere un libro Excel .xlsx")
    try:
        file=pd.ExcelFile(BytesIO(data))
    except Exception as exc:
        raise ValueError("No se pudo abrir el libro Excel") from exc
    expected={"01_Configuracion","02_Registro_Basico","03_Registro_Completo"}
    if not expected.issubset(file.sheet_names):
        raise ValueError(f"Faltan pestañas obligatorias: {sorted(expected-set(file.sheet_names))}")
    conf=pd.read_excel(file,sheet_name="01_Configuracion",header=4,usecols="A:B").dropna(subset=["CÓDIGO"])
    settings={str(k).strip():v for k,v in zip(conf.iloc[:,0],conf.iloc[:,1])}
    if str(settings.get("VERSION_ESQUEMA",""))!="1.0.0":
        raise ValueError("VERSION_ESQUEMA incompatible: se requiere 1.0.0")
    level=str(settings.get("NIVEL_REGISTRO","")).strip().upper()
    if level not in RECORD_SHEETS:
        raise ValueError("NIVEL_REGISTRO debe ser BASICO o COMPLETO")
    if str(settings.get("MODO_ANALISIS","")).strip().upper() != "SIMULACION_EMPIRICA":
        raise ValueError("Este importador procesa SIMULACION_EMPIRICA; la reproducción histórica es otro método")
    branch=str(settings.get("SUCURSAL_ID","")).strip()
    if not branch or branch.lower()=="nan":
        raise ValueError("SUCURSAL_ID es requerido")
    start=pd.to_datetime(settings.get("INICIO_OBSERVACION"),errors="coerce")
    end=pd.to_datetime(settings.get("FIN_OBSERVACION"),errors="coerce")
    if pd.isna(start) or pd.isna(end) or not start < end:
        raise ValueError("Definir INICIO_OBSERVACION y FIN_OBSERVACION válidos, ordenados y completos")
    sheets={}
    for n, (sheet, cols) in RECORD_SHEETS.items():
        frame=pd.read_excel(file,sheet_name=sheet,header=5,dtype={"registro_id":str},keep_default_na=True)
        if not set(cols).issubset(frame.columns):
            raise ValueError(f"{sheet}: faltan columnas oficiales")
        frame=frame.dropna(subset=["registro_id"],how="all")
        sheets[n]=frame
    other = "COMPLETO" if level=="BASICO" else "BASICO"
    if len(sheets[other])>0:
        raise ValueError(f"No mezclar niveles: la hoja {RECORD_SHEETS[other][0]} contiene registros")
    f=sheets[level]
    if len(f)<3:
        raise ValueError("Se requieren al menos tres llegadas registradas")
    if len(f)>100000:
        raise ValueError("Máximo 100.000 registros por carga")
    problems=[]
    warnings=[]
    values=[]
    durations=[]
    seen=set()
    client_ids=set()
    occupied={}
    for idx,r in f.iterrows():
        excel_row=int(idx)+7
        rid=str(r.get("registro_id","")).strip()
        if not rid or rid.lower()=="nan":
            problems.append(f"Fila {excel_row}: registro_id faltante");continue
        if rid in seen:
            problems.append(f"Fila {excel_row}: registro_id duplicado {rid}")
        seen.add(rid)
        if str(r.get("sucursal_id","")).strip()!=branch:
            problems.append(f"Fila {excel_row}: sucursal_id diferente de configuración")
        state=str(r.get("estado","")).strip().upper()
        if state not in VALID_STATES:
            problems.append(f"Fila {excel_row}: estado inválido {state}")
        t=pd.to_datetime(r.get("llegada_ts"),errors="coerce")
        if pd.isna(t) or not start<=t<end:
            problems.append(f"Fila {excel_row}: llegada fuera del intervalo observado")
            continue
        values.append(t)
        if level=="COMPLETO":
            client=str(r.get("cliente_anon","")).strip()
            if client and client.lower()!="nan":
                # Múltiples operaciones por un mismo cliente pueden ser válidas.
                client_ids.add(client)
            t0=pd.to_datetime(r.get("inicio_atencion_ts"),errors="coerce")
            t1=pd.to_datetime(r.get("fin_atencion_ts"),errors="coerce")
            exit_t=pd.to_datetime(r.get("salida_sin_atencion_ts"),errors="coerce")
            slot=str(r.get("ventanilla_id","")).strip()
            if state=="ATENDIDO":
                if pd.isna(t0) or pd.isna(t1) or t0<t or t1<=t0 or slot.lower() in {"nan",""}:
                    problems.append(f"Fila {excel_row}: ATENDIDO exige llegada <= inicio < fin y ventanilla")
                else:
                    durations.append((t1-t0).total_seconds()/60)
                    occupied.setdefault(slot,[]).append((t0,t1,excel_row))
                if not pd.isna(exit_t):
                    problems.append(f"Fila {excel_row}: ATENDIDO no debe tener salida sin atención")
            elif state in {"ABANDONO","RECHAZO"}:
                if pd.isna(exit_t) or exit_t<t:
                    problems.append(f"Fila {excel_row}: {state} exige hora de salida >= llegada")
                if not pd.isna(t0) or not pd.isna(t1):
                    problems.append(f"Fila {excel_row}: {state} no puede tener intervalos de atención")
            elif state=="SERVICIO_AL_CORTE":
                if pd.isna(t0) or slot.lower() in {"nan",""} or t0<t or not pd.isna(t1):
                    problems.append(f"Fila {excel_row}: SERVICIO_AL_CORTE exige inicio y ventanilla, sin fin")
            elif state=="ESPERA_AL_CORTE":
                if not pd.isna(t0) or not pd.isna(t1):
                    problems.append(f"Fila {excel_row}: ESPERA_AL_CORTE no debe tener servicio")
        else:
            secs=pd.to_numeric(r.get("servicio_seg"),errors="coerce")
            if state=="ATENDIDO":
                if pd.isna(secs) or not math.isfinite(float(secs)) or secs<=0:
                    problems.append(f"Fila {excel_row}: ATENDIDO exige servicio_seg positivo")
                else:
                    durations.append(float(secs)/60)
            elif not pd.isna(secs):
                problems.append(f"Fila {excel_row}: servicio_seg solo corresponde a ATENDIDO")
    if level=="COMPLETO":
        for slot,intervals in occupied.items():
            ordered=sorted(intervals)
            for (_,prev_finish,prev_row),(next_start,_,row) in zip(ordered,ordered[1:]):
                if next_start < prev_finish:
                    problems.append(f"Filas {prev_row}/{row}: solapamiento de atención en ventanilla {slot}")
    if problems:
        return {"valid":False,"errors":problems[:200],"warnings":warnings,"rows":len(f),
                "level":level,"arrival_samples":[],"service_samples":[]}
    values=sorted(values)
    # No remuestrear las pausas nocturnas como si fueran interarribos ordinarios.
    gaps=[(b-a).total_seconds()/60 for a,b in zip(values,values[1:]) if a.date()==b.date()]
    zeros=sum(v==0 for v in gaps)
    gaps=[v for v in gaps if v>0]
    if zeros:
        warnings.append(f"{zeros} llegadas simultáneas o con precisión insuficiente; se excluyeron interarribos cero")
    distinct_days=len({x.date() for x in values})
    if distinct_days < 5:
        warnings.append(f"Solo {distinct_days} día(s) representado(s): no se garantiza representatividad semanal")
    if len(durations)<100:
        warnings.append(f"Solo {len(durations)} atenciones completas con duración: verificar suficiencia estadística")
    if str(settings.get("CAPTURA_NO_ATENDIDOS","NO")).upper()!="SI":
        warnings.append("No se registraron necesariamente todas las pérdidas; los rechazos observados pueden estar sesgados")
    if len(gaps)<2 or len(durations)<2:
        return {"valid":False,"errors":["Muestra insuficiente: mínimo dos interarribos positivos y dos servicios completos"],
                "warnings":warnings,"rows":len(f),"level":level,"arrival_samples":[],"service_samples":[]}
    return {"valid":True,"errors":[],"warnings":warnings,"rows":len(f),"level":level,
            "arrival_samples":gaps,"service_samples":durations,
            "days":distinct_days,"captured_start":str(start),"captured_end":str(end),
            "avg_interarrival":sum(gaps)/len(gaps),"avg_service":sum(durations)/len(durations),
            "note":"Remuestreo exploratorio global. No preserva correlaciones/estacionalidad por franjas."}
