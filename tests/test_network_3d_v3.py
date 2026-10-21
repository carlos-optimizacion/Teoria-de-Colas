"""Regresión H3.1: topologías seriales, conservación y trazas WebGL reales."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"django_app"))
from portal.network_engine import simulate_network
from portal.network_v3 import evaluate_network
from network_three_scene import network_scene_html


def config(n, reps=2):
    stages=[{"name":f"Proceso {i+1}","service_min":3.0+i*.3,"servers":1+(i%3)}
            for i in range(n)]
    return {"arrival_min":2.0,"horizon":120,"replications":reps,
            "seed":2026,"stages":stages}


@pytest.mark.parametrize("n",[2,4,8,10])
def test_network_capacity_invariants_and_frame_entity_conservation(n):
    raw=config(n)
    a=evaluate_network(raw)
    assert len(a["stages"])==n
    assert a["replications_effective"]==2
    assert a["frames"][0]["kind"]=="start"
    assert a["frames"][-1]["kind"]=="end"
    assert a["frames"][-1]["t"]==120
    assert len(a["frames"])<=3000
    for fr in a["frames"]:
        assert len(fr["queues"])==n
        assert len(fr["busy"])==n
        assert len(fr["service_ids"])==n
        assert len(fr["queue_ids"])==n
        assert len(fr["arrived_stage"])==n
        assert len(fr["completed_stage"])==n
        for j in range(n):
            assert fr["busy"][j]==sum(cid is not None for cid in fr["service_ids"][j])
            assert len(fr["queue_ids"][j])<=min(10,fr["queues"][j])
            assert fr["arrived_stage"][j] >= fr["completed_stage"][j]
            if j:
                assert fr["arrived_stage"][j]==fr["completed_stage"][j-1]
            assert all(cid is not None for cid in fr["queue_ids"][j])
            assert all(cid not in fr["service_ids"][j] for cid in fr["queue_ids"][j])
    last=a["frames"][-1]
    assert last["arrivals"]==a["runs"][0]["arrivals"]
    assert last["completed"]==a["runs"][0]["completed"]
    assert sum(last["queues"])+sum(last["busy"])==a["runs"][0]["in_system_at_close"]
    assert a==evaluate_network(raw), "Las mismas semillas deben repetir exactamente la trayectoria"
    assert network_scene_html(a,preview=True).count('data-testid=')==0
    assert "Fotogramas del motor Python" in network_scene_html(a)


def test_too_many_stages_rejected():
    with pytest.raises(ValueError,match="entre 2 y 10"):
        simulate_network(config(11))


def test_browser_script_parses_and_payload_escapes_stage_names():
    raw=config(6,reps=1)
    raw["stages"][1]["name"]="Interacción </script> & validación"
    result=evaluate_network(raw)
    html=network_scene_html(result)
    assert "Interacción </script>" not in html
    assert "\\u003c/script\\u003e" in html
    assert 'id="stage"' in html and 'id="nodes"' in html
    assert 'data-source' not in html  # Se crea mediante los eventos del reproductor.
    assert 'stage").dataset.source="python-network-events"' in html
    if shutil.which("node"):
        script=re.search(r'<script type="module">(.*?)</script>',html,re.S).group(1)
        check=subprocess.run(["node","--input-type=module","--check"],input=script,
                             text=True,capture_output=True,timeout=20)
        assert check.returncode==0,check.stderr
