"""Vista integral Decision Lab 3.0: una pantalla de ingreso, múltiples motores."""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

DJANGO = Path(__file__).resolve().parent / "django_app"
if str(DJANGO) not in sys.path:
    sys.path.insert(0, str(DJANGO))

from portal.queue_v3 import MODELS, evaluate, optimize, optimize_shifts, replay_replica
from portal.empirical_v3 import import_workbook
from portal.challenge_engine import SCENARIOS
from bank_three_scene import bank_scene_html
from streamlit_sector_scenes import render_sector_scene, SECTOR_UI
from report_v3 import report_pdf, report_xlsx


LABELS = {"deterministic":"Determinística","parametric":"Estocástica paramétrica",
          "empirical":"Estocástica empírica (Excel)"}
OPTIONS = {
    "deterministic":["D/D/1","D/D/c"],
    "parametric":[m for m in MODELS if not m.startswith("D/")],
    "empirical":["G/G/1","G/G/c"],
}
FIELD_LABELS={"deterministic":"Separación exacta entre llegadas",
              "parametric":"Tasa media de llegadas",
              "empirical":"Distribución empírica de llegadas"}


def _plot(r, metric, label):
    values = r["series"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[e["t"] for e in values],
                             y=[e[metric] for e in values],name=label,
                             mode="lines",line_shape="hv"))
    fig.update_layout(height=235,margin=dict(l=20,r=10,b=28,t=12),
                      template="plotly_white",xaxis_title="Minutos simulados",
                      yaxis_title=label,showlegend=False)
    return fig


def run():
    st.header("Decision Lab 3.0 · Simulador multimodelo")
    state = st.session_state
    state.setdefault("v3_step","configure")
    state.setdefault("v3_result",None)
    state.setdefault("v3_payload",None)
    state.setdefault("v3_optimization",None)
    state.setdefault("v3_optimization_dynamic",None)
    st.caption("1. Configurar → 2. Validar → 3. Previsualizar → 4. Simular → 5. Analizar y reportar")

    if state.v3_step=="configure":
        st.subheader("1 · Ingreso de datos y modelo matemático")
        st.info("Primero ingresa y valida tus datos. El escenario 3D permanecerá oculto hasta guardar la configuración.")
        sc_options=list(SCENARIOS)
        sector=st.selectbox("Escenario operativo",sc_options,format_func=lambda k:SCENARIOS[k]["sector"],key="v3_sector")
        mode=st.radio("Tipo de simulación",list(LABELS),format_func=lambda k:LABELS[k],
                      horizontal=True,key="v3_mode")
        models=OPTIONS[mode]
        model=st.selectbox("Modelo matemático",models,key=f"v3_model_{mode}",help="Cada modelo exige distribuciones y supuestos propios.")
        special=model.startswith("M/G") or model.startswith("G/G")
        finite="/K" in model or "Erlang B" in model
        single=model.endswith("/1") or model.endswith("/1/K")
        cfg=SCENARIOS[sector]
        sample_data=None
        if mode=="empirical":
            st.markdown("**Datos reales estructurados**")
            file=st.file_uploader("Plantilla oficial Decision Lab (.xlsx), nivel básico o completo",
                                  type=["xlsx"],key="v3_excel",help="Solo se acepta la estructura oficial 1.0.0.")
            if file is not None:
                try:
                    sample_data=import_workbook(file.getvalue())
                    if sample_data["valid"]:
                        st.success(f"Validado: {sample_data['rows']} registros · {sample_data['level']} · {sample_data['days']} día(s)")
                        for issue in sample_data["warnings"][:10]:
                            st.warning(issue)
                    else:
                        st.error("Hay errores que impiden la simulación empírica:")
                        for issue in sample_data["errors"][:15]:
                            st.error(issue)
                except ValueError as exc:
                    st.error(str(exc))

        # Guided input: essential operational decisions visible first.
        # Model-specific distributions, capacity and costs are shown only when relevant.
        explain={
            "D/D/1":"Una ventanilla. Las llegadas y la duración de atención son fijas.",
            "D/D/c":"Llegadas espaciadas regularmente y atención de duración fija.",
            "M/M/1":"Una ventanilla, llegadas Poisson y atención exponencial.",
            "M/M/c":"Varias ventanillas, llegadas Poisson y atención exponencial.",
            "M/M/1/K":"Una ventanilla y capacidad limitada; las llegadas adicionales se rechazan.",
            "M/M/c/K":"Varias ventanillas y capacidad total limitada (cola + servicio).",
            "M/M/c/c (Erlang B)":"Sin sala de espera: si todos los puestos están ocupados se rechaza la llegada.",
            "M/G/1":"Una ventanilla: llegadas Poisson y duración de atención con distribución a elegir.",
            "M/G/c":"Varias ventanillas: llegadas Poisson y servicio con distribución a elegir.",
            "G/G/1":"Una ventanilla: procesos de llegadas y servicio generales.",
            "G/G/c":"Varias ventanillas: procesos de llegadas y servicio generales.",
        }
        st.caption("**Modelo seleccionado:** "+explain.get(model,model))
        st.markdown("**Paso 2 · Define la demanda, los recursos y la duración**")
        with st.form("v3_configuration"):
            customers=15
            interval=60.
            service=float(cfg["service_min"])
            if mode!="empirical":
                way=st.radio("¿Cómo prefieres describir las llegadas?",
                             ["Cantidad de clientes por intervalo","Tiempo entre llegadas"],
                             horizontal=True,help="Son dos formas alternativas de expresar la misma demanda media.")
                if way=="Cantidad de clientes por intervalo":
                    p1,p2=st.columns(2)
                    customers=p1.number_input(
                        "Clientes que llegan" if mode=="deterministic" else "Clientes esperados (en promedio)",
                        min_value=1,max_value=10000,value=15,step=1,
                        help="Determinística: cantidad programada. Estocástica: cantidad media, no un valor garantizado.")
                    interval=p2.number_input("Durante cuántos minutos",min_value=.1,max_value=10080.,
                                              value=60.,step=5.)
                    avg_gap=interval/customers
                else:
                    avg_gap=st.number_input(
                        "Tiempo entre llegadas (min)"
                        if mode=="deterministic" else "Tiempo medio entre llegadas (min)",
                        min_value=.005,max_value=10080.,value=4.,step=.5,
                        help="Determinística: el intervalo siempre es igual; estocástica: es un promedio.")
                st.caption(f"**Demanda configurada:** un cliente cada {avg_gap:.2f} min "
                           +("(exactamente)" if mode=="deterministic" else "(en promedio)"))
            else:
                avg_gap=float(sample_data["avg_interarrival"]) if sample_data and sample_data["valid"] else float(cfg["arrival_min"])
                service=float(sample_data["avg_service"]) if sample_data and sample_data["valid"] else float(cfg["service_min"])
                st.caption("Los intervalos entre llegadas y los tiempos de atención se calcularán desde el Excel. "
                           "No tienes que introducirlos ni elegir una distribución manualmente.")
                if sample_data and sample_data["valid"]:
                    st.metric("Interarribo observado (promedio)",f"{avg_gap:.2f} min")
                    st.metric("Servicio observado (promedio)",f"{service:.2f} min")
            p3,p4=st.columns(2)
            if mode=="empirical":
                p3.caption(f"Duración media de atención leída del Excel: **{service:.2f} min**")
            else:
                service=p3.number_input(
                    "Tiempo fijo de atención (min)" if mode=="deterministic" else "Tiempo medio de atención (min)",
                    min_value=.005,max_value=10080.,value=float(cfg["service_min"]),step=.5,
                    help="En un modelo D es exactamente este valor. En modelos estocásticos es la media.")
            if single:
                servers=1
                p4.caption("**Servidores: 1** · Este modelo matemático exige un único servidor.")
            else:
                servers=p4.number_input(
                    "Ventanillas / puestos de atención",min_value=1,
                    max_value=min(40,int(cfg["max_servers"])),
                    value=min(4,int(cfg["max_servers"])),step=1)
            p5,p6=st.columns(2)
            horizon=p5.number_input("Tiempo de simulación (min)",min_value=1,max_value=10080,
                                     value=480,step=30,help="La duración virtual de cada corrida; no la velocidad del 3D.")
            reps=p6.number_input("Número de réplicas",min_value=1,max_value=300,
                                  value=1 if mode=="deterministic" else 30,step=1,
                                  help="El modelo determinístico usa una sola trayectoria; los estocásticos comparan corridas.")
            capacity=int(servers)
            if finite:
                if "Erlang B" in model:
                    st.caption(f"**Capacidad: {servers}** (igual a los servidores; este modelo no admite cola).")
                else:
                    capacity=st.number_input("Capacidad máxima del sistema (K: espera + atención)",
                                           min_value=int(servers),max_value=100000,
                                           value=max(int(servers),int(cfg["capacity"])),
                                           help="Se rechazan nuevas llegadas si la capacidad total está ocupada.")
            arrival_dist="deterministic" if mode=="deterministic" else "exponential"
            service_dist="deterministic" if mode=="deterministic" else "exponential"
            arrival_cv=service_cv=1.
            if mode=="parametric" and (model.startswith("G/G") or special):
                with st.expander("Distribuciones del modelo · elegir solo cuando corresponda",expanded=True):
                    if model.startswith("G/G"):
                        da,ca=st.columns(2)
                        arrival_dist=da.selectbox("Tiempo entre llegadas: distribución",
                                                 ["exponential","gamma","lognormal","triangular"])
                        if arrival_dist in ("gamma","lognormal"):
                            arrival_cv=ca.number_input("CV de interarribo",.05,5.,1.,.05,
                                                        help="Desviación estándar dividida entre la media.")
                    if special:
                        ds,cs=st.columns(2)
                        service_dist=ds.selectbox("Servicio: distribución",
                                                  ["exponential","gamma","lognormal","triangular","deterministic"])
                        if service_dist in ("gamma","lognormal"):
                            service_cv=cs.number_input("CV del servicio",.05,5.,1.,.05,
                                                        help="Desviación estándar dividida entre la media.")
            else:
                st.caption("Las distribuciones matemáticas compatibles se configuran automáticamente.")
            with st.expander("Opciones avanzadas · SLA, costos y reproducibilidad",expanded=False):
                st.caption("Puedes usar los valores propuestos para explorar el modelo. "
                           "Modifícalos si necesitas evaluar objetivos reales o costos de operación.")
                a1,a2,a3=st.columns(3)
                sla_min=a1.number_input("Espera máxima permitida (min)",min_value=0.,max_value=10080.,
                                         value=float(cfg["sla_min"]),help="Umbral de espera para considerar que un cliente cumple el SLA.")
                sla_target=a2.number_input("Clientes que deben cumplir el SLA (%)",min_value=0.,
                                            max_value=100.,value=float(cfg["sla_target"]*100),step=1.,
                                            help="Ejemplo: 90 significa al menos el 90 % de los clientes admitidos.")
                seed=a3.number_input("Semilla para repetir los resultados",min_value=1,max_value=999999999,value=2026)
                b1,b2,b3=st.columns(3)
                server_hour=b1.number_input("Costo por servidor/hora (S/)",min_value=0.,
                                              max_value=100000.,value=float(cfg["staff_hour"]),step=1.)
                wait_hour=b2.number_input("Costo espera por cliente-hora (S/)",min_value=0.,
                                           max_value=100000.,value=float(cfg["wait_hour"]),step=1.)
                lost_cost=b3.number_input("Costo por cliente rechazado (S/)",min_value=0.,
                                           max_value=100000.,value=float(cfg["lost_cost"]),step=1.)
            save=st.form_submit_button("Guardar y validar configuración",type="primary",use_container_width=True)
        if save:
            if mode=="empirical" and (not sample_data or not sample_data["valid"]):
                st.error("La simulación está bloqueada hasta cargar un Excel válido.")
                return
            raw={"model":model,"mode":mode,"horizon":int(horizon),
                 "replications":int(reps),"seed":int(seed),"servers":int(servers),
                 "arrival_mean":float(avg_gap),"service_mean":float(service),
                 "sla_min":float(sla_min),"sla_target":float(sla_target)/100,
                 "server_hour":float(server_hour),"wait_hour":float(wait_hour),
                 "lost_cost":float(lost_cost),"arrival_dist":arrival_dist,
                 "service_dist":service_dist,"arrival_cv":arrival_cv,"service_cv":service_cv}
            if finite:
                raw["capacity"]=int(capacity)
            if mode=="empirical":
                if sample_data.get("arrival_profile") and int(horizon)!=sample_data.get("horizon"):
                    st.error("Para el muestreo por franjas el horizonte debe coincidir con HORIZONTE_SIM_MIN de la plantilla Excel.")
                    return
                raw["arrival_samples"]=sample_data["arrival_samples"]
                raw["service_samples"]=sample_data["service_samples"]
                if sample_data.get("arrival_profile"):
                    raw["arrival_profile"]=sample_data["arrival_profile"]
                    raw["profile_bin"]=sample_data["profile_bin"]
                raw["arrival_mean"]=sample_data["avg_interarrival"]
                raw["service_mean"]=sample_data["avg_service"]
                raw["empirical_quality"]={"rows":sample_data["rows"],"level":sample_data["level"],
                                          "warnings":sample_data["warnings"],"days":sample_data["days"],
                                          "sampling_method":sample_data.get("sampling_method"),
                                          "source_sha256":__import__("hashlib").sha256(file.getvalue()).hexdigest()}
            try:
                result=evaluate(raw)
            except (ValueError,RuntimeError) as exc:
                st.error(f"El motor rechazó los parámetros: {exc}")
                return
            state.v3_payload=raw
            state.v3_result=result
            state.v3_scenario=sector
            state.v3_optimization=None
            state.v3_optimization_dynamic=None
            state.v3_step="preview"
            st.rerun()
        return

    result=state.v3_result
    raw=state.v3_payload
    sector=state.v3_scenario
    model=result["model"]
    st.caption(f"Modelo: **{model}** · {LABELS[result['mode']]} · {result['horizon']} min · "
               f"{result['replications_requested']} réplica(s) solicitadas · "
               f"{result['replications_effective']} ejecutadas")
    if st.button("← Volver a ingresar datos"):
        state.v3_step="configure";state.v3_result=None;state.v3_optimization=None;st.rerun()
    config3d={"arrival_min":raw["arrival_mean"],"service_min":raw["service_mean"],
              "capacity":result["capacity"] if result["capacity"] is not None else "Sin límite",
              "duration":result["horizon"],"model":model,"sector":sector}
    if state.v3_step=="preview":
        st.subheader("2 · Vista previa: entorno construido sin movimiento")
        first=result["events"][0]
        components.html(bank_scene_html([first],config3d,preview=True),height=835,scrolling=False)
        st.caption("Vista previa 3D específica del sector. Los elementos de atención coinciden con la configuración guardada.")
        if st.button("▶ Iniciar simulación desde 0 min",type="primary",use_container_width=True):
            state.v3_step="run";st.rerun()
        return

    st.subheader("3 · Simulación y monitoreo")
    index=st.selectbox("Réplica a reproducir en Three.js",list(range(1,result["replications_effective"]+1)),key="v3_replay_index")
    visual_result=result
    if index>1:
        trajectory=replay_replica(raw,index)
        visual_result=dict(result)
        visual_result["events"]=trajectory["events"]
        visual_result["series"]=trajectory["series"]
        visual_result["selected_replica"]=index
    components.html(bank_scene_html(visual_result["events"],config3d),height=890,scrolling=False)
    st.caption("Escena 3D del sector seleccionado: reproducción temporal y gráficos del mismo flujo de eventos de Python.")
    st.markdown("**Monitoreo temporal de la primera réplica**")
    metric=st.selectbox("Gráfico",["queue","busy","arrivals","completed","avg_wait","utilization"],
                        format_func=lambda x:{"queue":"Cola Q(t)","busy":"Ocupación B(t)",
                        "arrivals":"Llegadas acumuladas","completed":"Atenciones completadas",
                        "avg_wait":"Espera media acumulada","utilization":"Utilización acumulada"}[x])
    st.plotly_chart(_plot(visual_result,metric,{"queue":"Clientes en cola","busy":"Servidores ocupados",
                  "arrivals":"Clientes","completed":"Clientes","avg_wait":"Minutos",
                  "utilization":"Proporción"}[metric]),use_container_width=True)
    st.subheader("4 · Resultados consolidados de réplicas")
    m=result["metrics"]
    cols=st.columns(4)
    for col,(title,val) in zip(cols,[("Wq",f"{m['avg_wait']:.2f} min"),
                                      ("Lq",f"{m['avg_queue']:.2f}"),
                                      ("SLA",f"{m['sla']*100:.1f}%"),
                                      ("Costo total",f"S/ {m['total_cost']:,.2f}")]):
        col.metric(title,val)
    st.caption("Indicadores consolidados de todas las réplicas, no estados instantáneos. "
               "El SLA incluye admitidos pendientes al cierre; los IC son exploratorios.")
    if result["replications_effective"]>1:
        df=pd.DataFrame(result["runs"])
        st.dataframe(df[["arrivals","completed","avg_wait","sla","utilization","total_cost"]],use_container_width=True)
        st.markdown("**Intervalos de confianza (aproximación normal, 95%)**")
        st.dataframe(pd.DataFrame.from_dict(result["confidence_95"],orient="index"),use_container_width=True)
    st.markdown("**Contraste con teoría de colas**")
    theory=result.get("theory",{})
    if theory.get("available"):
        st.dataframe(pd.DataFrame(theory["metrics"].items(),columns=["Indicador","Valor teórico"]),use_container_width=True)
        st.caption(theory["condition"])
    else:
        st.info(theory.get("reason","No hay solución analítica exacta para el modelo elegido."))
    st.subheader("5 · Optimizador automático")
    maxval=min(40,int(SCENARIOS[sector]["max_servers"]))
    if model in {"D/D/1","M/M/1","M/M/1/K","M/G/1","G/G/1"}:
        st.info("Este modelo define un solo servidor; selecciona su variante multiserver para optimizar dotación.")
    else:
        upper=st.number_input("Máximo de servidores a evaluar",min_value=1,max_value=maxval,
                              value=max(1,min(maxval, max(raw["servers"],6))))
        if st.button("Optimizar capacidad por SLA y costo",type="primary"):
            with st.spinner("Evaluando alternativas con semillas comparables..."):
                try:
                    state.v3_optimization=optimize(raw,int(upper))
                except ValueError as exc:
                    st.error(str(exc))
        if state.v3_optimization:
            solution=state.v3_optimization
            st.dataframe(pd.DataFrame(solution["alternatives"]),use_container_width=True)
            if solution["recommended"]:
                win=solution["recommended"]
                st.success(f"Menor costo total entre alternativas con SLA medio ≥ {solution['target']*100:.1f}%: "
                           f"{win['servers']} servidores, S/ {win['total_cost']:,.2f}.")
            else:
                st.warning("Ninguna dotación evaluada cumple la meta de SLA medio.")
            st.caption(solution["caveat"])
        st.markdown("**Optimización de dotación variable por franjas de 60 minutos**")
        st.caption("La búsqueda por turnos es heurística; evalúa costo total y SLA medio con semillas comparables. "
                   "Las atenciones en curso no se interrumpen cuando disminuye la dotación.")
        if st.button("Optimizar turnos por franjas",key="v3_opt_shifts"):
            if result["replications_effective"]>50 or result["horizon"]>1440:
                st.warning("Para evitar bloqueos interactivos, evalúa turnos con hasta 50 réplicas y 1440 minutos.")
            else:
                with st.spinner("Evaluando dotaciones por intervalos..."):
                    try:
                        state.v3_optimization_dynamic=optimize_shifts(raw,int(upper))
                    except ValueError as exc:
                        st.error(str(exc))
        if state.v3_optimization_dynamic:
            opt=state.v3_optimization_dynamic
            if opt["feasible"]:
                schedule=[{"Franja":i+1,"Inicio":60*i,"Fin":min(result["horizon"],60*(i+1)),
                           "Servidores":c} for i,c in enumerate(opt["schedule"])]
                st.dataframe(pd.DataFrame(schedule),use_container_width=True)
                st.success(f"Plan heurístico: SLA {opt['sla']*100:.2f}% · costo total S/ {opt['cost']:,.2f}.")
                st.caption(opt["caveat"])
            else:
                st.warning(opt["message"])
    st.subheader("6 · Reporteador de simulación")
    try:
        pdf_data=report_pdf(visual_result,state.v3_optimization,state.v3_optimization_dynamic)
        excel_data=report_xlsx(visual_result,state.v3_optimization,state.v3_optimization_dynamic)
    except Exception:
        import logging
        logging.exception("Fallo al generar el reporte Decision Lab 3.0")
        st.error("No se pudieron generar los reportes. Consulta el diagnóstico del servidor.")
        return
    p1,p2,p3=st.columns(3)
    p1.download_button("Informe PDF",data=pdf_data,
                       file_name="decision-lab-3-informe.pdf",mime="application/pdf",
                       use_container_width=True)
    p2.download_button("Resultados Excel",data=excel_data,
                       file_name="decision-lab-3-resultados.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)
    p3.download_button("Experimento JSON",data=json.dumps(
        {**visual_result,"optimization":state.v3_optimization,"optimization_dynamic":state.v3_optimization_dynamic},ensure_ascii=False,indent=2),
        file_name="decision-lab-3-reproducible.json",mime="application/json",use_container_width=True)
