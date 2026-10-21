import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"django_app"))

from portal.challenge_engine import SCENARIOS, evaluate_game
from streamlit_visual_logic import configured_station_count, station_descriptors

def test_visual_station_count_matches_configured_servers_in_all_scenarios():
    for scenario,cfg in SCENARIOS.items():
        for count in range(1,min(5,int(cfg["max_servers"]))+1):
            result=evaluate_game({
                "scenario":scenario,
                "staffing":[count]*8,
                "replications":1,
                "seed":2026,
            })
            frame=result["events"][0]
            assert frame["active"]==count,(scenario,count,frame["active"])
            assert configured_station_count(frame)==count,(scenario,count,station_descriptors(frame))

def test_inactive_empty_stations_are_hidden_but_draining_station_remains():
    frame={"active":1,"servers":[101,None,None,None]}
    visible=station_descriptors(frame)
    assert [x["number"] for x in visible]==[1]
    frame={"active":1,"servers":[101,202,None,None]}
    visible=station_descriptors(frame)
    assert [x["number"] for x in visible]==[1,2]
    assert visible[1]["configured"] is False
    assert visible[1]["draining"] is True
