"""Calidad H1: registro central y cuatro módulos de la plataforma."""
from copy import deepcopy

import pytest

from experiment_registry_v3 import (
    MAX_SNAPSHOTS, comparable, comparison_rows, register_experiment,
    snapshot_experiment,
)


RAW = {
    "model":"M/M/c/K","mode":"parametric","horizon":120,"replications":3,
    "seed":2026,"servers":4,"capacity":20,"arrival_mean":4.0,"service_mean":6.0,
    "server_hour":23.0,"wait_hour":13.0,
}
RESULT = {
    "model":"M/M/c/K","mode":"parametric","horizon":120,
    "replications_effective":3,"seed":2026,"servers":4,"capacity":20,
    "metrics":{"avg_wait":1.2,"avg_queue":.5,"sla":.95,
               "utilization":.31,"blocked":0,"total_cost":102.3},
    "method":"DES, horizonte finito","confidence_95":{"sla":{"low":.89,"high":.97}},
}


def test_snapshot_deterministic_and_no_original_mutation():
    before=deepcopy(RAW)
    s1=snapshot_experiment(RAW,RESULT,"banco")
    s2=snapshot_experiment(RAW,RESULT,"banco")
    assert s1==s2
    assert len(s1["id"])==12
    assert s1["source"]=="queue_v3"
    assert s1["mode"]=="parametric"
    assert RAW==before
    assert s1["metrics"]["avg_wait"]==1.2


def test_empirical_data_are_not_persisted():
    raw={**RAW,"mode":"empirical","model":"G/G/c",
         "arrival_samples":[1.0,3.0,5.0],"service_samples":[2.,7.]}
    result={**RESULT,"mode":"empirical","model":"G/G/c"}
    entry=snapshot_experiment(raw,result,"hospital")
    assert "arrival_samples" not in entry["parameters"]
    assert "service_samples" not in entry["parameters"]
    assert entry["parameters"]["arrival_samples_count"]==3
    assert entry["parameters"]["service_samples_count"]==2


def test_registry_idempotency_and_bounded_session_memory():
    snap=snapshot_experiment(RAW,RESULT,"banco")
    data=register_experiment([],snap)
    assert data==register_experiment(data,snap)
    for n in range(MAX_SNAPSHOTS+4):
        result={**RESULT,"seed":n}
        data=register_experiment(data,snapshot_experiment({**RAW,"seed":n},result,"banco"))
    assert len(data)==MAX_SNAPSHOTS
    assert len({x["id"] for x in data})==MAX_SNAPSHOTS


def test_comparison_units_and_validity_guards():
    one=snapshot_experiment(RAW,RESULT,"banco")
    two=snapshot_experiment({**RAW,"servers":3}, {**RESULT,"servers":3},"banco")
    rows=comparison_rows([one,two])
    assert rows[0]["SLA (%)"]==95.
    assert rows[0]["Wq (min)"]==1.2
    assert comparable([one,two])[0]
    diff_horizon=snapshot_experiment({**RAW,"horizon":240},{**RESULT,"horizon":240},"banco")
    assert not comparable([one,diff_horizon])[0]
    diff_sector=snapshot_experiment(RAW,RESULT,"hospital")
    assert not comparable([one,diff_sector])[0]
    assert not comparable([one])[0]


def test_reject_invalid_missing_and_nonfinite_metrics():
    with pytest.raises(ValueError):
        snapshot_experiment(RAW,{**RESULT,"metrics":{}},"banco")
    with pytest.raises(ValueError):
        snapshot_experiment(RAW,{**RESULT,"metrics":{**RESULT["metrics"],"sla":float("nan")}},"banco")
    with pytest.raises(ValueError):
        register_experiment([],{"bad":"item"})
