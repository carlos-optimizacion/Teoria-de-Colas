"""H3: invariantes contables y precisión de redes de cola en tándem."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"django_app"))
from portal.network_engine import simulate_network
from portal.network_v3 import evaluate_network


@pytest.mark.parametrize("stages",[
    [{"name":"A","service_min":3,"servers":1},{"name":"B","service_min":8,"servers":2}],
    [{"name":"Registro","service_min":5,"servers":2},
     {"name":"Triaje","service_min":9,"servers":1},
     {"name":"Consulta","service_min":6,"servers":3}],
    [{"name":"Ingreso","service_min":3,"servers":3},
     {"name":"Pago","service_min":4,"servers":1},
     {"name":"Atención","service_min":8,"servers":2},
     {"name":"Salida","service_min":2,"servers":3}],
])
def test_per_stage_and_global_flow_conservation(stages):
    raw={"arrival_min":2.5,"horizon":120,"seed":2026,"stages":stages}
    result=simulate_network(raw)
    assert result["arrivals"]==result["completed"]+result["in_system_at_close"]
    assert result["frames"][0]["t"]==0
    assert result["frames"][-1]["t"]==120
    assert len(result["stages"])==len(stages)
    for i,row in enumerate(result["stages"]):
        assert row["arrived"]==row["completed"]+row["in_stage_at_close"]
        assert row["in_stage_at_close"]==row["waiting_at_close"]+row["in_service_at_close"]
        if i:
            assert row["arrived"]==result["stages"][i-1]["completed"]
        else:
            assert row["arrived"]==result["arrivals"]
        assert 0<=row["utilization"]<=1
        assert row["avg_wait"]>=0 and row["avg_queue"]>=0


def test_replicas_aggregate_are_reproducible_and_no_fake_statistics():
    p={"arrival_min":3,"horizon":120,"replications":5,"seed":2026,
       "stages":[{"name":"A","service_min":4,"servers":2},
                 {"name":"B","service_min":7,"servers":2}]}
    a,b=evaluate_network(p),evaluate_network(p)
    assert a==b
    assert a["replications_effective"]==5
    assert len(a["runs"])==5
    assert len({x["seed"] for x in a["runs"]})==5
    assert a["runs"][0]["arrivals"]==a["runs"][0]["completed"]+a["runs"][0]["in_system_at_close"]
    assert a["metrics"]["arrivals"]==pytest.approx(sum(x["arrivals"] for x in a["runs"])/5,abs=1e-6)
    assert a["metrics"]["completed"]==pytest.approx(sum(x["completed"] for x in a["runs"])/5,abs=1e-6)
    assert len(a["stages"])==2
    assert 0<=a["bottleneck_index"]<2
    assert a["confidence_95"]["avg_system"]["low"] is not None
    assert "cola" in a["model"].lower() or "M/M/c" in a["model"]


def test_single_replica_intervals_are_null_and_large_seeds_work():
    p={"arrival_min":6,"horizon":120,"replications":1,"seed":999999999}
    one=evaluate_network(p)
    assert one["confidence_95"]["avg_system"]["low"] is None
    assert one["confidence_95"]["avg_system"]["high"] is None
    two=evaluate_network({**p,"replications":3})
    assert all(1<=x["seed"]<=999999999 for x in two["runs"])
    assert two["frames"][-1]["t"]==120


@pytest.mark.parametrize("reps",[0,41,2.4,True,"5"])
def test_invalid_replications_fail_closed(reps):
    with pytest.raises(ValueError,match="Réplicas"):
        evaluate_network({"replications":reps})


def test_stochastic_network_is_not_mislabeled_as_independent_stages():
    r=evaluate_network({"arrival_min":4,"horizon":180,"replications":2})
    assert r["engine"]=="network_engine"
    assert r["integration_contract"]=="v3"
    assert r["model"]=="Tándem M/M/c"
    assert "tándem" in r["method"].lower()
