"""Pruebas de integridad de la escena Banco 3D."""
import json
import re
import shutil
import subprocess

import pytest

from bank_three_scene import bank_scene_html


def make_frame(n, *, queue=None, servers=None):
    return {
        "t": 0, "kind": "start", "client": None,
        "active": n, "servers": servers if servers is not None else [None] * 8,
        "queue_ids": queue or [], "queue": len(queue or []),
        "busy": 0, "arrivals": 0, "completed": 0, "blocked": 0,
    }


def encoded_payload(html):
    match = re.search(r"const payload = (\{.*?\});\s*\nconst frames=", html, re.S)
    assert match, "El reproductor debe recibir una traza de eventos"
    return json.loads(match.group(1))


@pytest.mark.parametrize("count", range(1, 9))
def test_bank_3d_exact_server_count_from_backend(count):
    f = make_frame(count)
    data = encoded_payload(bank_scene_html([f], {
        "arrival_min": 4.0, "service_min": 6.0, "capacity": 24, "duration": 480,
    }, preview=True))
    assert data["config"]["servers"] == count
    assert data["frames"][0]["active"] == count
    assert data["preview"] is True
    assert len(data["frames"]) == 1


def test_bank_event_replay_does_not_generate_its_own_arrivals():
    initial = make_frame(1)
    next_frame = {**initial, "t": 2.3, "kind": "arrival", "client": 9,
                  "queue": 1, "queue_ids": [9], "arrivals": 1}
    html = bank_scene_html([initial, next_frame], {
        "arrival_min": 2.0, "service_min": 5.0, "capacity": 20,
    })
    data = encoded_payload(html)
    assert len(data["frames"]) == 2
    assert data["frames"][1]["queue_ids"] == [9]
    assert "f.queue_ids" in html
    assert "f.servers" in html
    assert "expovariate" not in html
    assert data["preview"] is False


def test_bank_json_escaping_does_not_close_html_script():
    initial = make_frame(2)
    initial["kind"] = "</script><h1>malicioso</h1>"
    html = bank_scene_html([initial], {})
    assert "<h1>malicioso</h1>" not in html
    assert encoded_payload(html)["frames"][0]["kind"] == initial["kind"]


def test_bank_scene_fails_without_servers_or_events():
    with pytest.raises(ValueError):
        bank_scene_html([], {})
    with pytest.raises(ValueError):
        bank_scene_html([make_frame(0)], {})


def test_browser_module_javascript_syntax():
    """Node checks parse errors in the exact embedded JS, when installed."""
    if shutil.which("node") is None:
        pytest.skip("Node.js no está instalado")
    html = bank_scene_html([make_frame(3)], {"arrival_min": 4, "service_min": 6})
    match = re.search(r'<script type="module">(.*?)</script>', html, re.S)
    assert match
    process = subprocess.run(
        ["node", "--input-type=module", "--check"],
        input=match.group(1), text=True, capture_output=True, timeout=20,
    )
    assert process.returncode == 0, process.stderr



@pytest.mark.parametrize("sector,profile", [
    ("banco","financial-branch"),
    ("hospital","emergency-department"),
    ("supermercado","grocery-checkout"),
    ("logistica","industrial-truck-yard"),
])
def test_four_operational_environments_are_distinct_and_share_python_events(sector,profile):
    initial=make_frame(4,servers=[None]*4)
    future={**initial,"t":5,"kind":"arrival","client":1,"queue":1,"queue_ids":[1],"arrivals":1}
    html=bank_scene_html([initial,future],{
        "sector":sector,"arrival_min":4,"service_min":6,"duration":60,"model":"M/M/c",
    })
    assert encoded_payload(html)["config"]["sector"]==sector
    assert encoded_payload(html)["frames"][-1]["arrivals"]==1
    assert "/*__ENVIRONMENT__*/" not in html
    assert "$('stage').dataset.environment" in html
    assert profile in html
    assert "stage.dataset.stationType" in html
    if sector=="logistica":
        assert "PATIO LOG" in html
        assert "fork" in html
        assert "const maxVisibleClients=sector==='logistica'?16:35" in html
    if sector=="hospital":
        assert "TRIAJE" in html
    if sector=="supermercado":
        assert "PROMOCIONES" in html
    if shutil.which("node"):
        script=re.search(r'<script type="module">(.*?)</script>',html,re.S).group(1)
        check=subprocess.run(["node","--input-type=module","--check"],input=script,
                             text=True,capture_output=True,timeout=20)
        assert check.returncode==0,check.stderr
