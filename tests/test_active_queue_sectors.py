"""Regresión del catálogo de sectores y su motor compartido de colas."""
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "django_app"))
from portal.challenge_engine import SCENARIOS, ACTIVE_SCENARIOS, evaluate_game
from portal.queue_v3 import evaluate
from bank_three_scene import bank_scene_html


EXPECTED = ("banco", "hospital", "supermercado", "logistica")


def _payload(html):
    m = re.search(r"const payload = (\{.*?\});\s*\nconst frames=", html, flags=re.S)
    assert m, "El entorno 3D no recibió la trayectoria Python"
    return json.loads(m.group(1))


def test_only_queue_compatible_sectors_are_selectable():
    assert ACTIVE_SCENARIOS == EXPECTED
    assert "fabrica" not in ACTIVE_SCENARIOS
    assert "fabrica" in SCENARIOS, "Conservar configuración histórica para futuro flujo continuo"
    assert len(set(ACTIVE_SCENARIOS)) == len(ACTIVE_SCENARIOS)
    for sector in ACTIVE_SCENARIOS:
        assert sector in SCENARIOS


@pytest.mark.parametrize("sector", EXPECTED)
def test_parametric_experiment_integrity_in_all_active_sectors(sector):
    cfg=SCENARIOS[sector]
    servers=min(3,cfg["max_servers"])
    spec={"model":"M/M/c/K","mode":"parametric","servers":servers,
          "capacity":max(servers,cfg["capacity"]),"horizon":60,
          "arrival_mean":cfg["arrival_min"],"service_mean":cfg["service_min"],
          "replications":4,"seed":2026,
          "sla_min":cfg["sla_min"],"sla_target":cfg["sla_target"],
          "server_hour":cfg["staff_hour"],"wait_hour":cfg["wait_hour"],
          "lost_cost":cfg["lost_cost"]}
    result=evaluate(spec)
    assert result["replications_effective"]==4
    assert result["events"][0]["active"]==servers
    assert result["events"][-1]["t"]==60
    assert result["metrics"]["total_cost"]>=0
    assert result["metrics"]["avg_wait"]>=0
    assert 0<=result["metrics"]["utilization"]<=1
    assert 0<=result["metrics"]["sla"]<=1
    assert all(frame["queue"]+frame["busy"]<=spec["capacity"] for frame in result["events"])
    for run in result["runs"]:
        assert run["arrivals"]==run["completed"]+run["blocked"]+run["unserved_at_close"]
    config={"arrival_min":spec["arrival_mean"],"service_min":spec["service_mean"],
            "capacity":spec["capacity"],"duration":60,"sector":sector,"model":spec["model"]}
    preview=_payload(bank_scene_html(result["events"],config,preview=True))
    playback=_payload(bank_scene_html(result["events"],config))
    assert preview["config"]["sector"]==sector
    assert preview["config"]["servers"]==servers
    assert preview["preview"] is True and len(preview["frames"])==1
    assert playback["preview"] is False
    assert playback["frames"][-1]["t"]==60
    assert playback["frames"][-1]["arrivals"]==result["events"][-1]["arrivals"]


@pytest.mark.parametrize("sector", EXPECTED)
def test_legacy_gamification_regression(sector):
    cfg=SCENARIOS[sector]
    result=evaluate_game({"scenario":sector,
                          "staffing":[min(3,cfg["max_servers"])]*8,
                          "replications":2,
                          "seed":2026})
    assert result["scenario"]==sector
    assert 0<=result["score"]<=100
    assert result["events"][0]["active"]==min(3,cfg["max_servers"])
