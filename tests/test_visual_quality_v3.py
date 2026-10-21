"""Calidad gráfica consistente para cuatro sectores y red multietapa."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"django_app"))
from bank_three_scene import bank_scene_html
from network_three_scene import network_scene_html
from portal.network_v3 import evaluate_network
from visual_quality_v3 import QUALITY_JS, embed_quality


@pytest.mark.parametrize("sector",["banco","hospital","supermercado","logistica"])
def test_sector_hd_controls_geometry_and_preserves_event_data(sector):
    raw=[
        {"t":0,"active":4,"kind":"start","servers":[None]*4,
         "queue":0,"queue_ids":[],"busy":0,"completed":0,"arrivals":0},
        {"t":4,"active":4,"kind":"arrival","servers":[None]*4,
         "queue":1,"queue_ids":[42],"busy":0,"completed":0,"arrivals":1},
    ]
    html=bank_scene_html(raw,{"sector":sector,"arrival_min":4,"service_min":6,
                              "duration":60,"model":"D/D/c"})
    assert "/*__QUALITY__*/" not in html
    assert "setupVisualQuality" in html
    assert html.count('id="quality"')==1
    assert 'data-render-scale' not in html  # Set at runtime from real capabilities
    assert "renderScale=density.toFixed(2)" in html
    assert "can.width=1024;can.height=256;" in html
    assert "ACESFilmicToneMapping" in html
    assert "t.queue_ids" not in html
    assert "arrivals" in html
    assert 'id="graph-queue"' in html
    assert "for(const [i,c] of counters)" in html
    if sector=="hospital":
        assert "features.medicalSigns=1" in html
    if sector=="supermercado":
        assert "features.hangingSigns=2" in html
    if sector=="logistica":
        assert "features.safetyMarkers=2" in html
    if sector=="banco":
        assert "features.turnMonitor=1" in html
    assert_valid_module(html)


def assert_valid_module(html):
    if shutil.which("node"):
        match=re.search(r'<script type="module">(.*?)</script>',html,re.S)
        assert match
        check=subprocess.run(["node","--input-type=module","--check"],
                              input=match.group(1),text=True,capture_output=True,timeout=20)
        assert check.returncode==0,check.stderr


def test_network_quality_preserves_python_events_and_node_states():
    result=evaluate_network({"arrival_min":5,"horizon":60,"replications":2,
                            "stages":[{"name":"A","service_min":4,"servers":2},
                                      {"name":"B","service_min":7,"servers":3}]})
    original=[dict(x) for x in result["frames"]]
    html=network_scene_html(result)
    assert result["frames"]==original
    assert html.count('id="quality"')==1
    assert "setupVisualQuality" in html
    assert "can.width=1280;can.height=200;" in html
    assert "signal.emissiveIntensity=.28" in html
    assert "payload.frames" in html
    assert "stage.dataset.visualQuality=level" in html
    assert_valid_module(html)


def test_visual_profiles_have_budget_modes_and_no_external_assets():
    for level in ["auto","high","balanced","economy"]:
        assert f"'{level}'" in QUALITY_JS
    for target in [512,1024,2048]:
        assert str(target) in QUALITY_JS
    assert "window.devicePixelRatio" in QUALITY_JS
    assert "THREE.PCFSoftShadowMap" in QUALITY_JS
    assert "http" not in QUALITY_JS
    with pytest.raises(ValueError):
        embed_quality("A page with no injection marker")
