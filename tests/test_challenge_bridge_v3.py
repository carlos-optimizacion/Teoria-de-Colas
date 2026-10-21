"""H2: motor central y motor extendido no se confunden ni duplican puntuaciones."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"django_app"))
from portal.challenge_engine import ACTIVE_SCENARIOS, SCENARIOS, evaluate_game
from portal.queue_v3 import evaluate as evaluate_queue


@pytest.mark.parametrize("sector",ACTIVE_SCENARIOS)
def test_challenge_baseline_routes_to_same_queue_v3_metrics(sector):
    cfg=SCENARIOS[sector]
    payload={
        "scenario":sector,"incident":"none",
        "arrival_min":cfg["arrival_min"],"service_min":cfg["service_min"],
        "capacity":cfg["capacity"],"staffing":[3]*8,
        "replications":3,"seed":2026,
        "staff_hour":cfg["staff_hour"],"wait_hour":cfg["wait_hour"],
        "lost_cost":cfg["lost_cost"],"sla_min":cfg["sla_min"],
        "sla_target":cfg["sla_target"],
        "service_distribution":"exponential","patience_min":0,
        "priority_share":0,"actions":[],
    }
    game=evaluate_game(payload)
    canonical=evaluate_queue({
        "model":"M/M/c/K","mode":"parametric","servers":3,
        "staffing":[3]*8,"replications":3,"seed":2026,
        "horizon":480,"capacity":cfg["capacity"],
        "arrival_mean":cfg["arrival_min"],"service_mean":cfg["service_min"],
        "server_hour":cfg["staff_hour"],"wait_hour":cfg["wait_hour"],
        "lost_cost":cfg["lost_cost"],"sla_min":cfg["sla_min"],
        "sla_target":cfg["sla_target"],
    })
    assert game["engine"]=="queue_v3"
    assert game["core_model"]=="M/M/c/K"
    assert game["metrics"]["abandoned"]==0
    for key,value in canonical["metrics"].items():
        assert game["metrics"][key]==value,(sector,key,value,game["metrics"].get(key))
    assert game["events"]==canonical["events"]
    assert game["series"]==canonical["series"]
    assert game["passes"]["budget"]==(game["metrics"]["staff_cost"]<=cfg["budget"])
    assert game["passes"]["sla"]==(game["metrics"]["sla"]>=cfg["sla_target"])
    assert 0<=game["score"]<=100


@pytest.mark.parametrize("sector",ACTIVE_SCENARIOS)
def test_incidents_keep_extended_model_and_conservation(sector):
    cfg=SCENARIOS[sector]
    r=evaluate_game({"scenario":sector,"staffing":[3]*8,"seed":2026,
                    "replications":2})
    assert r["engine"]=="challenge_extended"
    assert r["core_model"] is None
    assert 0<=r["score"]<=100
    assert r["metrics"]["arrivals"] == pytest.approx(
        r["metrics"]["completed"]+r["metrics"]["blocked"]
        +r["metrics"]["abandoned"]+r["metrics"]["unserved_at_close"]
    )
    assert r["events"][0]["active"]==3
    assert r["events"][-1]["t"]==480


def test_advanced_behavior_cannot_silently_become_canonical():
    p={"scenario":"banco","incident":"none","staffing":[3]*8,
       "replications":2}
    for change in ({"patience_min":4}, {"priority_share":.25},
                   {"actions":[{"minute":100,"servers":4}]},
                   {"service_distribution":"gamma","service_cv":.8}):
        r=evaluate_game({**p,**change})
        assert r["engine"]=="challenge_extended",change
    with pytest.raises(ValueError,match="incidente"):
        evaluate_game({**p,"incident":"meteorito"})


def test_zero_sla_target_is_safe():
    r=evaluate_game({"scenario":"banco","incident":"none","staffing":[3]*8,
                     "sla_target":0,"replications":2})
    assert r["engine"]=="queue_v3"
    assert 0<=r["score"]<=100
