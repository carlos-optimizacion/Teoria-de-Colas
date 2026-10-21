import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "django_app"))
import pytest
from portal.queue_v3 import validate, evaluate, optimize, optimize_shifts, replay_replica, simulate_one


BASE = {"model":"D/D/c","mode":"deterministic","horizon":60,"servers":2,
        "arrival_mean":5,"service_mean":6,"replications":15,"seed":2026}


def test_deterministic_reproducible_and_conservation():
    a=evaluate(BASE)
    b=evaluate(BASE)
    assert a==b
    assert a["replications_effective"] == 1
    assert a["confidence_95"]["sla"]["low"] is None
    assert a["metrics"]["arrivals"]==11
    r=a["runs"][0]
    assert r["arrivals"] == r["completed"] + r["blocked"] + r["unserved_at_close"]
    assert all(f["active"]==2 and len(f["servers"])==2 for f in a["events"])
    assert a["events"][-1]["t"] == 60


def test_finite_capacity_never_exceeded_and_erlang_b_zero_queue():
    x={**BASE,"model":"M/M/c/c (Erlang B)","mode":"parametric","arrival_mean":.2,
       "service_mean":10,"horizon":30,"capacity":999,"replications":4}
    a=evaluate(x)
    assert a["capacity"]==2
    assert a["metrics"]["blocked"] > 0
    assert all(f["queue"] == 0 for f in a["events"])
    for f in a["events"]:
        assert f["queue"]+f["busy"] <= 2


def test_model_compatibility_and_input_validation():
    with pytest.raises(ValueError):
        validate({**BASE,"model":"M/M/1","servers":2,"mode":"parametric"})
    with pytest.raises(ValueError):
        validate({**BASE,"model":"M/M/c/K","mode":"parametric","capacity":1})
    with pytest.raises(ValueError):
        validate({**BASE,"arrival_mean":-1})
    with pytest.raises(ValueError):
        validate({**BASE,"mode":"parametric"})
    with pytest.raises(ValueError):
        validate({**BASE,"replications":9999})


def test_general_stochastic_parametric_independent_replicas():
    cfg={"model":"G/G/c","mode":"parametric","horizon":120,"servers":3,
         "arrival_mean":3,"service_mean":5,"arrival_dist":"gamma","arrival_cv":.8,
         "service_dist":"lognormal","service_cv":1.3,"replications":12,"seed":789}
    a=evaluate(cfg)
    assert a==evaluate(cfg)
    assert a["replications_effective"] == 12
    assert len(set(r["arrivals"] for r in a["runs"])) > 1
    assert a["confidence_95"]["total_cost"]["low"] is not None


def test_empirical_samples_reproducible():
    cfg={"model":"G/G/c","mode":"empirical","horizon":90,"servers":2,
         "arrival_samples":[1.5,2.5,4,9,3],"service_samples":[4,6,8,11],
         "replications":8,"seed":35}
    a=evaluate(cfg)
    assert a==evaluate(cfg)
    assert a["events"][-1]["t"] == 90
    assert a["metrics"]["arrivals"]>0
    assert a["mode"]=="empirical"
    assert any(f["kind"]=="departure" for f in a["events"])


def test_optimization_exhaustive_feasible_result():
    cfg={"model":"M/M/c/K","mode":"parametric","horizon":240,"servers":3,
         "arrival_mean":2,"service_mean":5,"capacity":10,"replications":8,
         "seed":2026,"sla_target":.85}
    out=optimize(cfg,maximum=5)
    assert len(out["alternatives"]) == 5
    if out["recommended"]:
        ok=[v for v in out["alternatives"] if v["feasible_mean"]]
        assert out["recommended"]["total_cost"] == min(r["total_cost"] for r in ok)


def test_hourly_shift_schedule_matches_events_and_cost():
    config={"model":"D/D/c","mode":"deterministic","horizon":120,"servers":3,
            "staffing":[3,1],"arrival_mean":3,"service_mean":4,
            "server_hour":25,"wait_hour":0,"lost_cost":0}
    data=evaluate(config)
    events=data["events"]
    assert data["staffing"]==[3,1]
    assert events[0]["active"]==3
    assert any(f["kind"]=="shift" and f["active"]==1 and f["t"]==60 for f in events)
    assert data["metrics"]["staff_cost"]==100
    assert 0<=data["metrics"]["utilization"]<=1


def test_invalid_shift_plan_rejected():
    with pytest.raises(ValueError,match="Dotación por franjas"):
        validate({**BASE,"staffing":[1,2]})
    with pytest.raises(ValueError,match="Dotación de franja"):
        validate({**BASE,"staffing":[3]})


def test_shift_optimizer_bounded_and_reproducible():
    cfg={"model":"D/D/c","mode":"deterministic","horizon":120,"servers":3,
         "arrival_mean":12,"service_mean":3,"server_hour":25,
         "wait_hour":0,"lost_cost":0,"sla_target":.8}
    a=optimize_shifts(cfg,3)
    assert a==optimize_shifts(cfg,3)
    assert a["feasible"]
    assert len(a["schedule"])==2
    assert all(1<=c<=3 for c in a["schedule"])
    assert a["cost"]<=150


def test_selected_replica_same_seed_trace_and_metrics():
    cfg={"model":"M/M/c","mode":"parametric","servers":3,"horizon":60,
         "arrival_mean":3,"service_mean":4,"replications":4,"seed":40}
    r=evaluate(cfg)
    first=replay_replica(cfg,1)
    assert first["events"]==r["events"]
    third=replay_replica(cfg,3)
    assert third==replay_replica(cfg,3)
    assert third["events"]!=first["events"]
    with pytest.raises(ValueError):
        replay_replica(cfg,5)
