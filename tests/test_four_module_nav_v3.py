"""Regresión H1: menú simplificado e integración del centro de análisis."""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiment_registry_v3 import snapshot_experiment

EXPECTED=("Simulador 3D","Desafíos gerenciales","Red de colas","Análisis y reportes")


def _app():
    app=AppTest.from_file(str(ROOT/"streamlit_app.py"))
    app.run(timeout=60)
    assert not app.exception,app.exception
    return app


def test_four_sections_only_with_no_lost_routes():
    app=_app()
    nav=next(x for x in app.radio if x.label=="Navegación")
    assert nav.options==list(EXPECTED)
    for section in EXPECTED:
        next(x for x in app.radio if x.label=="Navegación").set_value(section)
        app.run(timeout=60)
        assert not app.exception,(section,app.exception)


def test_registered_runs_in_analytics_comparison():
    raw={"model":"M/M/c","mode":"parametric","horizon":480,
         "replications":20,"seed":2026,"servers":2,"arrival_mean":5,"service_mean":6}
    base={"model":"M/M/c","mode":"parametric","horizon":480,
          "replications_effective":20,"seed":2026,"servers":2,"capacity":None,
          "metrics":{"avg_wait":1.5,"avg_queue":.3,"sla":.9,"utilization":.6,
                     "total_cost":250,"blocked":0},"confidence_95":{}}
    first=snapshot_experiment(raw,base,"banco")
    second=snapshot_experiment({**raw,"servers":3},{**base,"servers":3,
                                "metrics":{**base["metrics"],"avg_wait":.5,
                                           "total_cost":260}},"banco")
    app=_app()
    app.session_state["v3_registry"]=[first,second]
    next(x for x in app.radio if x.label=="Navegación").set_value("Análisis y reportes")
    app.run(timeout=60)
    assert not app.exception,app.exception
    assert any(x.label=="Corridas a comparar" for x in app.multiselect)
    assert any(x.label=="Descargar comparación CSV" for x in app if x.type=="download_button")
    radio=next(x for x in app.radio if x.label=="Espacio de análisis")
    radio.set_value("Herramientas clásicas")
    app.run(timeout=60)
    assert not app.exception,app.exception
    assert any(x.label=="Herramienta heredada" for x in app.selectbox)
