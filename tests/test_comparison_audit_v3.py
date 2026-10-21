"""H4: comparar únicamente experimentos económicamente homogéneos."""
from copy import deepcopy
from experiment_registry_v3 import comparable, audit_export

def sample(i=1):
    return {"id":str(i),"sector":"banco","model":"M/M/c","mode":"parametric",
            "horizon_min":480,"replications":10,"servers":i,"capacity":None,
            "parameters":{"server_hour":23,"wait_hour":13,"lost_cost":60,
                          "sla_min":10,"sla_target":.9},
            "metrics":{"total_cost":300+i,"avg_wait":2.5,"avg_queue":1.2,"sla":.95,
                       "utilization":.6}}

def test_comparison_same_assumptions():
    a,b=sample(1),sample(2)
    ok,reason=comparable([a,b])
    assert ok,reason
    payload=audit_export([a,b])
    assert payload["schema"]=="astalanka-comparison-v1"
    assert payload["comparable_for_cost"] is True
    assert len(payload["summary_rows"])==2
    assert payload["runs"][0]["parameters"]["sla_target"]==.9

def test_comparison_rejects_incompatible_economic_assumptions():
    a=sample(1)
    for field,value in [("sector","hospital"),("model","G/G/c"),
                        ("mode","empirical"),("horizon_min",360)]:
        b=sample(2);b[field]=value
        assert not comparable([a,b])[0],field
    for field in ("server_hour","wait_hour","lost_cost","sla_min","sla_target"):
        b=sample(2);b["parameters"][field]+=1
        assert not comparable([a,b])[0],field

def test_comparison_audit_preserves_originals():
    a,b=sample(1),sample(2)
    exported=audit_export([a,b])
    exported["runs"][0]["parameters"]["server_hour"]=999
    assert a["parameters"]["server_hour"]==23
