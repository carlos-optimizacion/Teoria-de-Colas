"""H4: recomendaciones SLA/costo, comparabilidad y Excel auditables."""
from copy import deepcopy
from io import BytesIO
from zipfile import ZipFile
import pytest

from experiment_registry_v3 import snapshot_experiment, comparable, recommend_comparison
from comparison_xlsx_v3 import comparison_xlsx

BASE={"model":"M/M/c/K","mode":"parametric","horizon":120,"replications":8,
      "seed":2026,"servers":3,"capacity":12,"arrival_mean":4.,
      "service_mean":6.,"arrival_dist":"exponential","service_dist":"exponential",
      "sla_min":10.,"sla_target":.9,"server_hour":25.,"wait_hour":13.,
      "lost_cost":60.}
RES={"model":"M/M/c/K","mode":"parametric","horizon":120,"replications_effective":8,
     "seed":2026,"servers":3,"capacity":12,
     "metrics":{"avg_wait":4.,"avg_queue":1.5,"sla":.85,"utilization":.61,
                "blocked":1,"total_cost":100.},
     "method":"DES, horizonte finito"}


def experiment(servers,cost,sla,**kwargs):
    cfg={**BASE,"servers":servers,**kwargs}
    res={**RES,"model":cfg["model"],"servers":servers,"metrics":{**RES["metrics"],"total_cost":cost,"sla":sla}}
    return snapshot_experiment(cfg,res,"banco")


def test_recommendation_requires_sla_and_not_lowest_unrestricted_cost():
    cheap=experiment(2,60,.80)
    good=experiment(4,120,.95)
    high=experiment(5,155,.99)
    assert comparable([cheap,good,high])[0]
    verdict=recommend_comparison([cheap,good,high])
    assert verdict["valid"]
    assert verdict["recommended"]==good["id"]
    assert verdict["target"]==.9
    assert cheap["id"] not in verdict["feasible"]
    assert good["id"] in verdict["feasible"]
    assert verdict["cost"]==120
    assert "no se demuestra" in verdict["caveat"].lower()


def test_incompatible_assumptions_never_yield_winner():
    base=experiment(3,110,.94)
    for different in [
        experiment(4,80,.99,arrival_mean=3.),
        experiment(4,80,.99,service_mean=10.),
        experiment(4,80,.99,server_hour=80.),
        experiment(4,80,.99,sla_target=.98),
        experiment(4,80,.99,horizon=240),
        experiment(4,80,.99,model="M/M/1"),
    ]:
        verdict=recommend_comparison([base,different])
        assert not verdict["valid"]
        assert verdict["recommended"] is None


def test_no_feasible_alternative_is_explicit():
    low=experiment(2,90,.3)
    other=experiment(4,180,.5)
    result=recommend_comparison([low,other])
    assert result["valid"]
    assert result["recommended"] is None
    assert result["feasible"]==[]


def test_workbook_has_comparison_assumptions_and_traceability():
    rows=[experiment(3,110,.93),experiment(4,150,.99)]
    exported=comparison_xlsx(rows)
    assert exported[:2]==b"PK"
    with ZipFile(BytesIO(exported)) as z:
        xml=z.read("xl/workbook.xml").decode("utf-8")
        assert all(name in xml for name in ("Comparacion","Supuestos","Trazabilidad"))
        data="".join(z.read(name).decode("utf-8") for name in z.namelist()
                     if name.startswith("xl/worksheets/sheet"))
        assert rows[0]["id"] in z.read("xl/sharedStrings.xml").decode("utf-8")
        assert "formula" not in data.lower() or "<f>" not in data
    with pytest.raises(ValueError):
        comparison_xlsx([])


def test_empirical_source_mismatch_blocks_monetary_recommendation():
    one=experiment(3,100,.96,empirical_quality={"source_sha256":"aaa"})
    two=experiment(4,80,.98,empirical_quality={"source_sha256":"bbb"})
    assert not comparable([one,two])[0]
