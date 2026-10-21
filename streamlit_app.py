from __future__ import annotations
import base64, json, math, sys, time
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT=Path(__file__).resolve().parent
DJANGO_APP=ROOT/"django_app"
if str(DJANGO_APP) not in sys.path:
    sys.path.insert(0,str(DJANGO_APP))

from portal.challenge_engine import SCENARIOS, ACTIVE_SCENARIOS, evaluate_game
from portal.network_engine import simulate_network
from portal.network_v3 import evaluate_network
from queue_core import (
    mms_from_minutes,mmsk_from_minutes,mg1_from_minutes,dd1_sequence,
    economic_cost,evaluate_mms_capacity,recommend_mms_capacity,erlang_b
)
from streamlit_visual_logic import station_descriptors
from streamlit_sector_scenes import SECTOR_UI, render_sector_scene, configured_units
from bank_three_scene import bank_scene_html
import streamlit.components.v1 as components
from streamlit_v3 import run as run_decision_lab_v3
from experiment_registry_v3 import comparison_rows, comparable, recommend_comparison
from comparison_xlsx_v3 import comparison_xlsx

st.set_page_config(page_title="Decision Lab 3.0",page_icon="◈",layout="wide",initial_sidebar_state="expanded")

SCENE_DIR=DJANGO_APP/"static"/"img"/"scenarios"
MODELS=["M/M/1","M/M/s","M/M/s/K","M/M/1/c","M/M/s/c","Erlang B","M/G/1","D/D/1"]

def metric_cards(items,columns=4):
    cards=[]
    for label,value,kind in items:
        cards.append(f'<div class="kpi-card {kind}"><small>{label}</small><b>{value}</b></div>')
    st.markdown(f'<div class="kpi-grid cols-{columns}">'+"".join(cards)+'</div>',unsafe_allow_html=True)

def progress_html(value,label):
    pct=max(0,min(100,float(value)*100))
    st.markdown(f'<div class="dl-progress"><div class="dl-progress-head"><span>{label}</span><b>{pct:.0f}%</b></div><div class="dl-progress-track"><i style="width:{pct:.1f}%"></i></div></div>',unsafe_allow_html=True)

def workflow_stepper(phase):
    phases=["configure","preview","simulate","finished"]
    current=phases.index(phase) if phase in phases else 0
    labels=["1 · Configurar","2 · Construir","3 · Simular","4 · Evaluar"]
    items=[]
    for i,label in enumerate(labels):
        cls="done" if i<current else ("active" if i==current else "pending")
        items.append(f'<div class="flow-step {cls}"><span>{i+1}</span><b>{label.split(" · ",1)[1]}</b></div>')
    st.markdown('<div class="workflow-stepper">'+"<i>→</i>".join(items)+'</div>',unsafe_allow_html=True)

def css():
    st.markdown("""
    <style>
    .stApp{background:#F5F8FB;color:#12324F}.block-container{padding-top:.5rem;max-width:1600px}
    section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0B2D4F,#08243F);color:white}
    section[data-testid="stSidebar"] *{color:#EAF5FF}
    .dl-top{display:flex;justify-content:space-between;align-items:center;background:white;border:1px solid #DDE8F0;border-radius:16px;padding:12px 16px;margin-bottom:10px}
    .dl-brand{font-size:1.35rem;font-weight:900;color:#0F3E67}.dl-brand small{display:block;font-size:.72rem;font-weight:600;color:#70849A}
    .scene-card{background:white;border:2px solid #DCE8EF;border-radius:14px;overflow:hidden}.scene-card.selected{border-color:#1F83E1;box-shadow:0 0 0 3px #C8E3FC}
    .scene-caption{padding:8px 10px;font-weight:850;color:#153B63}.scene-caption small{display:block;color:#657C91;font-weight:500}
    .sim-head{display:flex;justify-content:space-between;gap:12px;align-items:center;background:#fff;border:1px solid #DDE8EF;border-radius:14px 14px 0 0;padding:12px 15px}
    .ops-shell{background:white;border:1px solid #dbe7ee;border-radius:16px 16px 0 0;overflow:hidden;box-shadow:0 8px 24px #153d5b12;margin-top:8px}.ops-head{display:grid;grid-template-columns:minmax(280px,1.5fr) 150px repeat(3,125px);gap:8px;align-items:center;padding:12px 14px}.ops-title{display:flex;align-items:center;gap:10px}.ops-icon{display:grid;place-items:center;width:42px;height:42px;border-radius:11px;background:#e7f3ff;color:#176fa6;font-size:22px}.ops-title h2{margin:0;font-size:1.05rem;color:#123f63}.ops-title p{margin:2px 0 0;font-size:.7rem;color:#6f8291}.ops-time{border-left:1px solid #dce7ee;padding-left:10px}.ops-time small,.ops-time span{display:block;font-size:.65rem;color:#718595}.ops-time b{display:block;font-size:1rem;color:#123f63;margin:2px 0}.ops-mini{border-radius:10px;padding:9px 10px;text-align:center}.ops-mini small{font-size:.62rem;display:block}.ops-mini b{font-size:1.15rem;display:block;margin-top:2px}.ops-mini.ok{background:#e9f8ef;color:#167849}.ops-mini.info{background:#eaf4ff;color:#176ba4}.ops-mini.warn{background:#fff0f0;color:#b54449}.scene-banner{height:150px;position:relative;overflow:hidden;background:#dcebf1}.scene-banner img{width:100%;height:100%;object-fit:cover;display:block}.scene-banner-shade{position:absolute;left:0;bottom:0;right:0;padding:12px 18px;background:linear-gradient(0deg,#0d345ab8,transparent);color:white}.scene-banner-shade b{display:block;font-size:1rem}.scene-banner-shade span{font-size:.72rem}
    .panel-title{background:white;border:1px solid #dfe8ee;border-radius:12px 12px 0 0;padding:10px 12px;margin-top:8px}.panel-title b,.panel-title span{display:block}.panel-title b{color:#153f61}.panel-title span{font-size:.68rem;color:#708494;margin-top:2px}
    .scenario-context{display:flex;align-items:center;justify-content:space-between;gap:16px;background:linear-gradient(100deg,#123f62,#1b6e86);color:white;padding:13px 17px}.scenario-context b,.scenario-context span{display:block}.scenario-context b{font-size:.9rem;letter-spacing:.08em}.scenario-context span{font-size:.68rem;color:#d5eaf3;margin-top:2px}.configured-capacity{text-align:center;min-width:130px;background:#ffffff14;border:1px solid #ffffff2b;border-radius:10px;padding:7px 12px}.configured-capacity small,.configured-capacity strong{display:block}.configured-capacity small{font-size:.5rem;letter-spacing:.08em;color:#cfe8f3}.configured-capacity strong{font-size:1.45rem;line-height:1.05;color:white}
    .sim-head h2{font-size:1.2rem;margin:0;color:#103D66}.sim-head p{margin:2px 0 0;font-size:.78rem;color:#657C91}
    .facility{background:linear-gradient(180deg,#EEF6F8,#DCEBEF);border-left:1px solid #DDE8EF;border-right:1px solid #DDE8EF;padding:10px 14px}
    .process-wrap{background:#eef5f8;border:1px solid #d6e4eb;border-top:0;padding:12px 14px 15px}.process-status{display:flex;align-items:center;gap:8px;background:white;border:1px solid #dce7ed;border-radius:10px;padding:8px 11px;margin-bottom:10px;font-size:.72rem}.process-status b{color:#173f60}.process-status>span:last-child{color:#61798b}.state-dot{width:9px;height:9px;border-radius:50%;background:#91a3b1;box-shadow:0 0 0 4px #91a3b126}.state-dot.running{background:#22a361;box-shadow:0 0 0 4px #22a36122;animation:pulse 1s infinite}.state-dot.paused{background:#e2a322}.state-dot.finished{background:#1776ba}.process-flow{display:grid;grid-template-columns:1fr 44px 1.4fr 44px 2.4fr 44px 1fr;align-items:stretch;gap:4px}.process-node{background:white;border:1px solid #d7e4eb;border-radius:12px;padding:10px;text-align:center;min-height:160px;position:relative;overflow:hidden}.process-node>b{display:block;font-size:.75rem;color:#153e60;margin-top:3px}.process-node>small{display:block;font-size:.62rem;color:#708493;margin:3px 0 8px}.node-icon{font-size:1.25rem;color:#2678a8;font-weight:900}.flow-arrow{display:grid;place-items:center;color:#7894a8;font-size:1.8rem;font-weight:900}.people-row{display:flex;flex-wrap:wrap;justify-content:center;gap:6px}.person{width:32px;height:38px;display:inline-flex;flex-direction:column;align-items:center;justify-content:center}.person i{width:16px;height:16px;border-radius:50%;background:#2e77aa;display:block;box-shadow:0 13px 0 3px #2e77aa}.person em{font-size:.52rem;font-style:normal;font-weight:900;color:white;transform:translateY(-7px);z-index:2}.person.serving i{background:#23955f;box-shadow:0 13px 0 3px #23955f}.moving-slot{height:52px;display:grid;place-items:center}.moving-in{animation:arrive 1.1s ease-in-out infinite alternate}.moving-out{animation:depart 1.1s ease-in-out infinite alternate}.station-grid{display:flex;flex-wrap:wrap;gap:7px;justify-content:center}.station{min-width:86px;min-height:80px;border-radius:10px;border:2px solid #9cc7da;background:#eff8fc;padding:7px;display:flex;flex-direction:column;align-items:center;justify-content:center}.station b{font-size:.65rem;color:#153e60}.station small{font-size:.56rem;color:#607889}.station.busy{border-color:#4b9ac1;background:#e3f4fb}.station.free{border-color:#72bf94;background:#edf9f2}.station.closed{border-color:#c7a273;background:#f8f2ea}.station-icon{font-size:1.1rem;font-weight:900}.empty-state,.flow-placeholder{font-size:.65rem;color:#8a9aa6}.journey-progress{height:25px;background:#edf3f6;position:relative;border-top:1px solid #dbe6ec}.journey-progress i{display:block;height:5px;background:linear-gradient(90deg,#1d7fca,#44b9e9);transition:width .35s ease}.journey-progress span{position:absolute;top:8px;font-size:.55rem;color:#6a7f8e}.start-label{left:10px}.end-label{right:10px}.finish-card{display:flex;justify-content:space-between;align-items:center;gap:18px;background:linear-gradient(120deg,#0c4a70,#14718a);color:white;border-radius:14px;padding:14px 18px;margin:10px 0}.finish-card span{font-size:.58rem;letter-spacing:.12em;color:#cfe9f4}.finish-card h3{margin:2px 0;font-size:1rem;color:white}.finish-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}.finish-grid div{background:#ffffff14;border:1px solid #ffffff22;border-radius:9px;padding:8px 10px;text-align:center}.finish-grid small,.finish-grid b{display:block}.finish-grid small{font-size:.55rem;color:#d5ebf3}.finish-grid b{font-size:.95rem;color:white}.section-separator{display:flex;justify-content:space-between;align-items:end;margin:17px 0 4px}.section-separator b{font-size:.72rem;letter-spacing:.08em;color:#174d6e}.section-separator span{font-size:.65rem;color:#7a8d9a}
    @keyframes pulse{0%{box-shadow:0 0 0 2px #22a36122}70%{box-shadow:0 0 0 8px #22a36100}100%{box-shadow:0 0 0 2px #22a36122}}@keyframes arrive{from{transform:translateX(-20px);opacity:.35}to{transform:translateX(14px);opacity:1}}@keyframes depart{from{transform:translateX(-10px);opacity:1}to{transform:translateX(22px);opacity:.25}}
    .facility-grid{display:grid;grid-template-columns:1fr 2fr;gap:12px}
    .zone{background:#FFFFFFE8;border:1px solid #CDDFE8;border-radius:12px;padding:10px;min-height:200px}
    .zone-title{font-size:.72rem;font-weight:900;color:#3A6078;letter-spacing:.05em}.queue-people,.servers{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
    .client{display:inline-grid;place-items:center;width:31px;height:31px;border-radius:50%;background:#A9D9F6;border:2px solid white;box-shadow:0 3px 7px #315D7440;font-size:.65rem;font-weight:900;color:#104669}
    .client.serving{background:#9AE3BC}.station{display:flex;flex-direction:column;gap:4px;align-items:center;min-width:96px;padding:8px;border-radius:10px;border:2px solid #94CAB7;background:#ECF8F2;font-size:.68rem}.station.busy{background:#E5F3FC;border-color:#7CB9D8}.station.closed{background:#F6F0EA;border-color:#D7A96C}
    .panel{background:white;border:1px solid #DFE8EF;border-radius:14px;padding:14px;margin-bottom:10px}
    .workflow-stepper{display:grid;grid-template-columns:1fr 22px 1fr 22px 1fr 22px 1fr;align-items:center;margin:8px 0 12px}.workflow-stepper>i{text-align:center;color:#91a7b5;font-style:normal;font-weight:900}.flow-step{display:flex;align-items:center;gap:8px;background:white;border:1px solid #dae6ed;border-radius:11px;padding:9px 11px;color:#718492}.flow-step span{display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:#e8eff3;font-size:.65rem;font-weight:900}.flow-step b{font-size:.7rem}.flow-step.active{border-color:#2b8dc2;box-shadow:0 0 0 3px #cfe9f666;color:#145b80}.flow-step.active span{background:#2187bd;color:white}.flow-step.done{background:#edf8f2;border-color:#b9dec9;color:#26744f}.flow-step.done span{background:#39a46d;color:white}
    .workflow-head{background:white;border:1px solid #dbe7ee;border-radius:16px;padding:18px 20px;margin:8px 0 14px;box-shadow:0 7px 20px #173d5b0e}.workflow-head span{font-size:.6rem;letter-spacing:.12em;font-weight:900;color:#2b7ba8}.workflow-head h2{margin:3px 0 4px;color:#123f62}.workflow-head p{margin:0;color:#6b8192;font-size:.78rem}.workflow-head.preview{border-left:5px solid #2595c6}.config-help{background:#edf6fb;border:1px solid #d4e7f1;border-radius:12px;padding:13px 15px;margin-top:12px}.config-help b,.config-help span,.config-help small{display:block}.config-help b{color:#164d6b}.config-help span{color:#337290;font-size:.76rem;margin:4px 0}.config-help small{color:#7b8d98}
    .sector-scene{border:1px solid #d5e3ea;border-radius:15px;overflow:hidden;background:#e9f2f5;margin:10px 0 12px;box-shadow:0 10px 26px #113d5b12}.sector-scene-head{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;color:white}.sector-scene-head>div:first-child{display:grid;grid-template-columns:auto 1fr;column-gap:9px;align-items:center}.sector-big-icon{font-size:1.6rem;grid-row:1/3}.sector-scene-head b{font-size:.95rem}.sector-scene-head small{font-size:.62rem;opacity:.85}.sector-capacity{text-align:center;min-width:125px;background:#ffffff18;border:1px solid #ffffff2b;border-radius:10px;padding:6px 10px}.sector-capacity small,.sector-capacity strong,.sector-capacity span{display:block}.sector-capacity small{font-size:.5rem;letter-spacing:.08em}.sector-capacity strong{font-size:1.35rem;line-height:1}.sector-capacity span{font-size:.6rem;margin-top:2px}
    .sector-flow{display:grid;grid-template-columns:1fr 36px 1.35fr 36px 2.4fr 36px 1fr;gap:4px;align-items:stretch;padding:13px;background:linear-gradient(180deg,#f7fbfd,#edf4f7)}.sector-zone{position:relative;background:white;border:1px solid #d9e5eb;border-radius:12px;padding:11px;text-align:center;min-height:190px}.sector-zone>b,.sector-zone>small{display:block}.sector-zone>b{font-size:.76rem;color:#173f60}.sector-zone>small{font-size:.61rem;color:#708391;margin:3px 0 9px}.zone-kicker{position:absolute;left:8px;top:7px;font-size:.52rem;font-weight:900;color:#9badb8}.sector-arrow{display:grid;place-items:center;font-size:1.65rem;color:#7593a6;font-weight:900}.sector-slot{height:72px;display:grid;place-items:center;margin-top:17px}.sector-people-row{display:flex;flex-wrap:wrap;justify-content:center;align-content:start;gap:7px;min-height:108px}.sector-person{display:inline-flex;flex-direction:column;align-items:center;justify-content:center;width:34px;height:43px}.sector-person i{display:grid;place-items:center;width:17px;height:17px;border-radius:50%;background:#327cae;color:#327cae;font-style:normal;font-size:.7rem;box-shadow:0 14px 0 3px #327cae}.sector-person em{transform:translateY(-8px);font-style:normal;font-size:.5rem;font-weight:900;color:white;z-index:2}.sector-person-fabrica i{border-radius:4px;background:#705aa6;color:white;box-shadow:0 14px 0 3px #705aa6}.sector-person-logistica i{border-radius:3px;background:#596f7f;color:white;box-shadow:0 14px 0 3px #596f7f}.sector-person.serving i{background:#23945e;color:#23945e;box-shadow:0 14px 0 3px #23945e}.service-zone{min-width:0}.sector-flow>*{min-width:0}.sector-units{display:grid;gap:8px;justify-content:center;align-items:stretch;width:100%;box-sizing:border-box}.sector-units.units-1{grid-template-columns:minmax(120px,170px)}.sector-units.units-2{grid-template-columns:repeat(2,minmax(100px,1fr))}.sector-units.units-3{grid-template-columns:repeat(3,minmax(86px,1fr))}.sector-units.units-4{grid-template-columns:repeat(2,minmax(100px,1fr))}.sector-units.units-5,.sector-units.units-6,.sector-units.units-7,.sector-units.units-8{grid-template-columns:repeat(3,minmax(86px,1fr))}.sector-unit{width:100%;min-width:0;box-sizing:border-box;min-height:92px;border:2px solid #9bc7d9;border-radius:10px;padding:7px;display:flex;flex-direction:column;justify-content:center;align-items:center;background:#f4fafc;overflow:hidden}.sector-unit-name{font-size:.63rem;font-weight:900;color:#164b69}.sector-unit small{font-size:.52rem;font-weight:900;margin-top:5px}.sector-unit.free{border-color:#79be97;background:#edf9f2}.sector-unit.busy{border-color:#4c9ac2;background:#e7f4fb}.sector-unit.closing{border-color:#d19b5f;background:#fff4e7}.sector-unit-symbol{font-size:1.35rem;color:#4b7890;margin:6px 0}.bank-window,.hospital-box,.checkout-lane,.inspection-station,.loading-dock{width:58px;height:33px;margin:6px 0 4px;position:relative;display:grid;place-items:center;font-size:.48rem;font-weight:900;letter-spacing:.05em}
    .bank-window{border:3px solid #2d6e9a;border-bottom-width:8px;background:#dcecf7;color:#23597c}.bank-window:before{content:"";position:absolute;top:-8px;left:6px;right:6px;height:5px;background:#173f62;border-radius:3px}.bank-window i{position:absolute;bottom:-7px;width:12px;height:9px;border-radius:50%;background:#436e8b}
    .hospital-box{border:3px solid #54a798;border-radius:9px;background:#effbf8;color:#267c6d}.hospital-box i{font-style:normal;font-size:1rem;color:#2e9d83;position:absolute;right:4px;top:0}
    .checkout-lane{border:2px solid #cf7e2b;background:#fff4e7;color:#9c5615}.checkout-lane i{position:absolute;left:3px;right:18px;bottom:5px;height:7px;background:repeating-linear-gradient(90deg,#60717f 0 5px,#aeb9c0 5px 10px)}.checkout-lane span{position:absolute;right:2px;top:3px;writing-mode:vertical-rl;font-size:.4rem}
    .inspection-station{border:2px dashed #6f65a1;background:#f2effb;color:#594e8c}.inspection-station i{font-style:normal;font-size:1rem}.inspection-station:after{content:"";position:absolute;left:-9px;right:-9px;bottom:-5px;height:5px;background:repeating-linear-gradient(90deg,#6d7180 0 7px,#c0c2cb 7px 14px)}
    .loading-dock{border:3px solid #557789;background:#eaf1f4;color:#3d5e6f}.loading-dock i{position:absolute;left:8px;right:8px;bottom:4px;height:13px;background:#8fa7b3;border-top:4px solid #526b78}.loading-dock:before{content:"";position:absolute;left:-13px;bottom:-4px;width:14px;height:8px;background:#526b78}
    .config-summary-title{display:flex;justify-content:space-between;align-items:center;margin:18px 0 4px;padding:10px 12px;background:#f0f7fb;border:1px solid #d5e7f0;border-radius:10px}.config-summary-title b{color:#164f70}.config-summary-title span{font-size:.68rem;color:#6c8190}
    .simulation-lock{background:#eef7f2;border:1px solid #cfe4d7;border-left:5px solid #39a46d;border-radius:10px;padding:9px 12px;margin-bottom:8px}.simulation-lock b,.simulation-lock span{display:block}.simulation-lock b{color:#28684c;font-size:.76rem}.simulation-lock span{color:#5f796d;font-size:.66rem;margin-top:2px}
    .sector-stage{position:relative;overflow:hidden;background:#eef4f6}.scene-decor{height:72px;position:relative;border-bottom:1px solid #d7e3e9;overflow:hidden}
    .bank-decor{background:linear-gradient(#eaf3f9 0 58%,#d9e8f1 58%)}.bank-sign{position:absolute;left:18px;top:12px;font-weight:900;color:#1d5378;letter-spacing:.12em}.ticket-kiosk{position:absolute;left:38%;bottom:8px;background:#214f6e;color:white;border-radius:6px;padding:5px 10px;text-align:center;font-size:.5rem}.ticket-kiosk b{font-size:.72rem}.digital-board{position:absolute;right:20px;top:10px;background:#17354a;color:#bff3c6;padding:5px 9px;border-radius:4px;font-size:.48rem}.chair-row{position:absolute;left:16%;bottom:6px;display:flex;gap:8px}.chair-row i{display:block;width:20px;height:11px;background:#7e9fb1;border-radius:4px 4px 2px 2px;border-bottom:7px solid #5f7f91}
    .hospital-decor{background:linear-gradient(#effbf8 0 58%,#deeee9 58%)}.triage-desk{position:absolute;left:18px;bottom:7px;border:2px solid #3c9785;background:white;color:#277565;padding:7px 15px;border-radius:5px;font-size:.55rem;font-weight:900}.medical-cross{position:absolute;right:20px;top:8px;color:#2a9b82;font-size:2rem;font-weight:900}.hospital-corridor{position:absolute;left:48%;right:12%;bottom:0;height:16px;background:repeating-linear-gradient(90deg,#b7d7cf 0 18px,#e8f4f1 18px 36px)}
    .market-decor{background:linear-gradient(#fff8ef 0 58%,#efe3d5 58%)}.aisle{position:absolute;left:18px;top:9px;display:flex;gap:5px}.aisle i{width:28px;height:41px;background:repeating-linear-gradient(#c3843e 0 5px,#f1c586 5px 10px);border:2px solid #9b692f}.cart-icon{position:absolute;left:39%;bottom:8px;font-size:1.6rem}.queue-rail{position:absolute;right:15%;bottom:9px;width:150px;height:2px;background:#cc8b45;box-shadow:0 -16px 0 #cc8b45}.market-sign{position:absolute;right:18px;top:9px;background:#ce7d27;color:white;padding:5px 9px;border-radius:4px;font-size:.5rem;font-weight:900}
    .factory-decor{background:linear-gradient(#f0eff7 0 58%,#dbdae5 58%)}.conveyor{position:absolute;left:20px;right:34%;bottom:13px;height:10px;background:#6f7280;display:flex;justify-content:space-around;align-items:center}.conveyor i{width:10px;height:10px;border-radius:50%;background:#c8cad2}.qc-sign{position:absolute;right:18px;top:9px;background:#59527f;color:white;padding:5px 9px;font-size:.5rem;font-weight:900}.safety-line{position:absolute;left:0;right:0;bottom:0;height:5px;background:repeating-linear-gradient(45deg,#f5c02e 0 10px,#303030 10px 20px)}.factory-light{position:absolute;right:22%;bottom:12px;color:#3cba6d}
    .logistics-decor{background:linear-gradient(#eaf1f4 0 55%,#cddbe0 55%)}.gate-house{position:absolute;left:15px;bottom:7px;background:white;border:2px solid #557789;padding:8px 12px;font-size:.5rem;font-weight:900;color:#426274}.yard-lanes{position:absolute;left:34%;right:28%;bottom:6px;display:flex;justify-content:space-around}.yard-lanes i{display:block;width:3px;height:40px;background:#fff}.truck-shape{position:absolute;right:18%;bottom:7px;width:48px;height:19px;background:#647d8a}.truck-shape:after{content:"";position:absolute;right:-14px;bottom:0;width:15px;height:14px;background:#455d69}.truck-shape i,.truck-shape:before{content:"";position:absolute;bottom:-5px;width:9px;height:9px;border-radius:50%;background:#253a44}.truck-shape i{left:8px}.truck-shape:before{right:-6px}.dock-sign{position:absolute;right:15px;top:8px;background:#496c7d;color:white;padding:5px 9px;font-size:.5rem;font-weight:900}

    .sector-banco .sector-scene-head{background:linear-gradient(100deg,#144a7a,#236ea3)}.sector-banco .service-zone{background:linear-gradient(180deg,#fff,#edf5fb)}.sector-banco .sector-unit{border-bottom-width:7px}
    .sector-hospital .sector-scene-head{background:linear-gradient(100deg,#18736d,#26a394)}.sector-hospital .service-zone{background:linear-gradient(180deg,#f7fffd,#eaf8f4)}.sector-hospital .sector-unit{border-radius:18px 18px 7px 7px}
    .sector-supermercado .sector-scene-head{background:linear-gradient(100deg,#a85d17,#dc8a2d)}.sector-supermercado .service-zone{background:linear-gradient(180deg,#fffaf4,#fff0df)}.sector-supermercado .sector-unit{border-left-width:7px}
    .sector-fabrica .sector-scene-head{background:linear-gradient(100deg,#514c80,#7772aa)}.sector-fabrica .service-zone{background:repeating-linear-gradient(135deg,#f9f8ff,#f9f8ff 14px,#f2f0fa 14px,#f2f0fa 28px)}.sector-fabrica .sector-unit{border-style:dashed}
    .sector-logistica .sector-scene-head{background:linear-gradient(100deg,#315d72,#4f879b)}.sector-logistica .service-zone{background:linear-gradient(180deg,#f7fafb,#e9f0f3)}.sector-logistica .sector-unit{border-radius:4px;border-top-width:8px}
    .moving-in{animation:arrive 1s ease-in-out infinite alternate}.moving-out{animation:depart 1s ease-in-out infinite alternate}
    .achievement{display:inline-block;background:#FFF1BE;color:#805C09;border-radius:99px;padding:5px 9px;margin:2px;font-size:.72rem;font-weight:800}
    .status-ok{background:#E8F8EF;border-left:5px solid #1B9158;padding:9px 12px;border-radius:9px}.status-warn{background:#FFF1E1;border-left:5px solid #D98225;padding:9px 12px;border-radius:9px}

    .kpi-grid{display:grid;gap:10px;margin:10px 0 14px}.kpi-grid.cols-4{grid-template-columns:repeat(4,minmax(0,1fr))}.kpi-grid.cols-5{grid-template-columns:repeat(5,minmax(0,1fr))}.kpi-grid.cols-6{grid-template-columns:repeat(6,minmax(0,1fr))}
    .kpi-card{background:#fff;border:1px solid #dce7ee;border-radius:13px;padding:12px 14px;box-shadow:0 5px 14px #133f5f0d}.kpi-card small{display:block;color:#6f8392;font-size:.7rem}.kpi-card b{display:block;color:#123f63;font-size:1.4rem;margin-top:3px}.kpi-card.ok{background:#eaf9ef}.kpi-card.info{background:#edf6ff}.kpi-card.warn{background:#fff0f0}.kpi-card.gold{background:#fff7dc}
    .dl-progress{margin:10px 0}.dl-progress-head{display:flex;justify-content:space-between;font-size:.73rem;color:#dcecff;margin-bottom:5px}.dl-progress-track{height:9px;background:#173d5b;border-radius:99px;overflow:hidden}.dl-progress-track i{display:block;height:100%;background:linear-gradient(90deg,#39a4ff,#73c9ff);border-radius:99px}
    #MainMenu{visibility:hidden}footer{visibility:hidden}
    [data-testid="stSidebarNav"]{display:none!important}
    header[data-testid="stHeader"]{background:transparent}
    @media(max-width:1200px){.process-flow{grid-template-columns:1fr 30px 1.3fr 30px 2fr 30px 1fr}.sector-flow{grid-template-columns:1fr 26px 1.2fr 26px 2fr 26px 1fr}.ops-head{grid-template-columns:1fr 140px}.ops-mini{display:none}}@media(max-width:900px){.sector-units.units-3,.sector-units.units-5,.sector-units.units-6,.sector-units.units-7,.sector-units.units-8{grid-template-columns:repeat(2,minmax(96px,1fr))}.sector-flow{grid-template-columns:1fr}.sector-arrow{transform:rotate(90deg);min-height:25px}.sector-zone{min-height:130px}.facility-grid{grid-template-columns:1fr}.dl-top{align-items:flex-start;flex-direction:column}.kpi-grid.cols-4,.kpi-grid.cols-5,.kpi-grid.cols-6{grid-template-columns:repeat(2,minmax(0,1fr))}.ops-head{grid-template-columns:1fr}.ops-time{border-left:0;padding-left:0}.scene-banner{height:110px}}
    </style>
    """,unsafe_allow_html=True)

def init_state():
    defaults={
        "scenario":"banco","result":None,"frame":0,"actions":[],"score_history":[],"v3_registry":[],
        "xp":0,"coins":0,"level":1,"completed":set(),"saved":{},"profile_name":"Carlos",
        "sim_status":"ready","sim_speed":1,"sim_phase":"configure","sim_screen":"config","pending_payload":None,
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v

def update_progress(result):
    key=result["scenario"]
    if key not in st.session_state.completed and result["passes"]["budget"] and result["passes"]["sla"]:
        st.session_state.completed.add(key);st.session_state.xp+=100;st.session_state.coins+=100
    else:
        st.session_state.xp+=5;st.session_state.coins+=2
    st.session_state.level=1+st.session_state.xp//500

def sidebar():
    with st.sidebar:
        st.markdown("## ◈ DECISION LAB 3.0")
        st.caption("Teoría de Colas en la Práctica")
        section=st.radio("Navegación",["Simulador 3D","Desafíos gerenciales","Red de colas","Análisis y reportes"],label_visibility="collapsed")
        st.divider()
        st.markdown(f"**{st.session_state.profile_name}** · Nivel {st.session_state.level}")
        progress_html(min(1,(st.session_state.xp%500)/500),f"{st.session_state.xp} XP · ★ {st.session_state.coins}")
        st.session_state.completed.intersection_update(ACTIVE_SCENARIOS)
        st.caption(f"Desafíos dominados: {len(st.session_state.completed)}/{len(ACTIVE_SCENARIOS)}")
        return section

def topbar():
    st.markdown(f"""<div class="dl-top"><div class="dl-brand">◈ DECISION LAB 3.0<small>Simulación, analítica y gamificación de sistemas de espera</small></div>
    <div><b>{st.session_state.profile_name}</b> · Nivel {st.session_state.level} &nbsp; <b>★ {st.session_state.coins}</b></div></div>""",unsafe_allow_html=True)

def scenario_gallery():
    """Solo escenarios de espera discreta; producción se tratará aparte."""
    if st.session_state.scenario not in ACTIVE_SCENARIOS:
        st.session_state.scenario = ACTIVE_SCENARIOS[0]
        st.session_state.result = None
        st.session_state.sim_phase = "configure"
        st.session_state.sim_screen = "config"
    cols=st.columns(len(ACTIVE_SCENARIOS))
    for col,key in zip(cols,ACTIVE_SCENARIOS):
        cfg = SCENARIOS[key]
        with col:
            path=SCENE_DIR/f"{key}.svg"
            if path.exists():st.image(str(path),use_container_width=True)
            if st.button(f"{cfg['sector']}\n\n{cfg['name']}",key=f"scene_{key}",use_container_width=True,type="primary" if st.session_state.scenario==key else "secondary"):
                st.session_state.scenario=key;st.session_state.result=None;st.session_state.frame=0;st.session_state.sim_status="ready";st.session_state.sim_phase="configure";st.session_state.sim_screen="config";st.session_state.pending_payload=None;st.rerun()

def event_text(frame):
    kind=frame.get("kind","")
    cid=frame.get("client")
    messages={
        "start":"La jornada está preparada. Pulsa Iniciar para comenzar.",
        "arrival":f"Cliente {cid} llega al sistema y busca atención.",
        "departure":f"Cliente {cid} termina su atención y sale del sistema.",
        "abandon":f"Cliente {cid} abandona la cola por superar su paciencia.",
        "action":"Se aplica una decisión de cambio de dotación.",
        "incident_start":"Ocurre un incidente operativo que modifica la capacidad o la demanda.",
        "incident_end":"Finaliza el incidente y la operación vuelve a su condición programada.",
        "end":"La jornada terminó. Revisa el resultado final."
    }
    return messages.get(kind,f"Evento operativo: {kind or 'sin evento'}")

def facility_html(frame,status):
    queue=list(frame.get("queue_ids",[]))
    servers=list(frame.get("servers",[]))
    active=int(frame.get("active",0))
    kind=frame.get("kind","")
    cid=frame.get("client")
    qhtml="".join(f'<span class="person qperson" title="Cliente {x}"><i>●</i><em>{x}</em></span>' for x in queue[:14]) or "<span class='empty-state'>Sin clientes esperando</span>"
    stations=[]
    for item in station_descriptors(frame):
        i=item["number"]-1;cust=item["client"];configured=item["configured"];draining=item["draining"]
        if draining:
            cls="closed busy"
            body=f'<span class="person serving"><i>●</i><em>{cust}</em></span><small>Cierre pendiente</small>'
        elif cust is not None:
            cls="busy"
            body=f'<span class="person serving"><i>●</i><em>{cust}</em></span><small>Atendiendo</small>'
        else:
            cls="free";body="<span class='station-icon'>✓</span><small>Libre</small>"
        stations.append(f'<div class="station {cls}" data-station="{i+1}" data-configured="{str(configured).lower()}"><b>Puesto {i+1}</b>{body}</div>')
    incoming = f'<span class="person moving-in"><i>●</i><em>{cid}</em></span>' if kind=="arrival" and cid else "<span class='flow-placeholder'>—</span>"
    outgoing = f'<span class="person moving-out"><i>●</i><em>{cid}</em></span>' if kind=="departure" and cid else "<span class='flow-placeholder'>—</span>"
    badge={"ready":"PREPARADO","running":"EN CURSO","paused":"PAUSADO","finished":"FINALIZADO"}.get(status,status.upper())
    return f"""<div class="process-wrap">
      <div class="process-status"><span class="state-dot {status}"></span><b>{badge}</b><span>{event_text(frame)}</span></div>
      <div class="process-flow">
        <div class="process-node arrivals"><div class="node-icon">↓</div><b>LLEGADAS</b><small>{frame.get('arrivals',0)} acumuladas</small><div class="moving-slot">{incoming}</div></div>
        <div class="flow-arrow"><span>→</span></div>
        <div class="process-node queue-node"><div class="node-icon">≋</div><b>COLA</b><small>{frame.get('queue',0)} esperando</small><div class="people-row">{qhtml}</div></div>
        <div class="flow-arrow"><span>→</span></div>
        <div class="process-node service-node"><div class="node-icon">▦</div><b>SERVICIO</b><small>{active} servidor{"es" if active!=1 else ""} configurado{"s" if active!=1 else ""} · {frame.get('busy',0)} ocupado{"s" if frame.get('busy',0)!=1 else ""}</small><div class="station-grid">{''.join(stations)}</div></div>
        <div class="flow-arrow"><span>→</span></div>
        <div class="process-node exit-node"><div class="node-icon">✓</div><b>SALIDA</b><small>{frame.get('completed',0)} atendidos</small><div class="moving-slot">{outgoing}</div></div>
      </div>
    </div>"""

def scene_data_uri(key):
    path=SCENE_DIR/f"{key}.svg"
    if not path.exists():
        return ""
    raw=base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{raw}"

def default_result(key):
    cfg=SCENARIOS[key]
    payload={"scenario":key,"staffing":[min(4,int(cfg["max_servers"]))]*8,"replications":10,"seed":2026,
             "arrival_min":cfg["arrival_min"],"service_min":cfg["service_min"],"capacity":cfg["capacity"],
             "staff_hour":cfg["staff_hour"],"wait_hour":cfg["wait_hour"],"sla_min":cfg["sla_min"],
             "sla_target":cfg["sla_target"],"patience_min":0,"priority_share":0,
             "service_distribution":"exponential","service_cv":1,"actions":[]}
    return evaluate_game(payload)

def run_challenge_ui():
    key=st.session_state.scenario
    cfg=SCENARIOS[key]
    ui=SECTOR_UI[key]
    scenario_gallery()

    # ---------------------------
    # PANTALLA A: CONFIGURACIÓN
    # ---------------------------
    if st.session_state.sim_screen=="config":
        phase="preview" if st.session_state.pending_payload else "configure"
        workflow_stepper(phase)
        draft=st.session_state.pending_payload or {
            "scenario":key,"staffing":[min(4,int(cfg["max_servers"]))]*8,"replications":10,"seed":2026,
            "arrival_min":cfg["arrival_min"],"service_min":cfg["service_min"],"capacity":cfg["capacity"],
            "staff_hour":cfg["staff_hour"],"wait_hour":cfg["wait_hour"],"sla_min":cfg["sla_min"],
            "sla_target":cfg["sla_target"],"patience_min":0,"priority_share":0,
            "service_distribution":"exponential","service_cv":1,"actions":[],"incident":cfg["incident"]
        }
        st.markdown(f"""<div class="workflow-head"><span>CONFIGURACIÓN DEL ESCENARIO</span><h2>{ui['title']} · ingresar datos primero</h2>
        <p>La simulación no se mostrará hasta que guardes estos parámetros y pulses <b>Abrir simulación</b>.</p></div>""",unsafe_allow_html=True)

        with st.form("strict_config_form",clear_on_submit=False):
            c1,c2,c3,c4=st.columns(4)
            arrival=c1.number_input("Interarribo promedio (min)",.1,240.0,float(draft["arrival_min"]),.1)
            service=c2.number_input("Servicio promedio (min)",.1,240.0,float(draft["service_min"]),.1)
            servers=c3.number_input(f"Número de {ui['unit_plural']}",1,int(cfg["max_servers"]),int(draft["staffing"][0]),1)
            capacity=c4.number_input("Capacidad total",1,1000,int(draft["capacity"]),1)
            c5,c6,c7,c8=st.columns(4)
            staff_cost=c5.number_input("Costo servidor / hora",0.0,10000.0,float(draft["staff_hour"]),1.0)
            wait_cost=c6.number_input("Costo espera / cliente-h",0.0,10000.0,float(draft["wait_hour"]),1.0)
            sla_min=c7.number_input("Espera SLA máxima (min)",.1,240.0,float(draft["sla_min"]),.5)
            sla_target=c8.number_input("SLA objetivo",0.0,1.0,float(draft["sla_target"]),.01)
            with st.expander("Comportamiento avanzado",expanded=False):
                a1,a2,a3,a4=st.columns(4)
                patience=a1.number_input("Paciencia media (0 = sin abandono)",0.0,240.0,float(draft.get("patience_min",0)),1.0)
                priority=a2.number_input("Proporción prioritaria",0.0,1.0,float(draft.get("priority_share",0)),.05)
                distributions=["exponential","deterministic","gamma","lognormal"]
                dist=a3.selectbox("Distribución del servicio",distributions,index=distributions.index(draft.get("service_distribution","exponential")))
                cv=a4.number_input("CV del servicio",.05,4.0,float(draft.get("service_cv",1)),.05)
            incident_labels={"demanda":"Pico de demanda (+65%)","ausencia":"Ausencia temporal de un servidor",
                             "averia":"Avería temporal","none":"Sin incidentes (motor central)"}
            choices=list(dict.fromkeys([cfg["incident"],"none"]))
            incident=st.selectbox("Incidente del desafío",choices,
                format_func=lambda x:incident_labels[x],
                index=choices.index(draft.get("incident",cfg["incident"])) if draft.get("incident",cfg["incident"]) in choices else 0,
                help="Sin incidentes, servicio exponencial y sin abandono ni prioridad: se utiliza queue_v3. "
                     "Las extensiones del desafío conservan el motor especializado.")
            reps=st.slider("Réplicas estadísticas",1,50,int(draft["replications"]))
            save_config=st.form_submit_button("Guardar y validar configuración",type="primary",use_container_width=True)

        if save_config:
            payload={"scenario":key,"staffing":[int(servers)]*8,"replications":int(reps),"seed":2026,
                     "arrival_min":float(arrival),"service_min":float(service),"capacity":int(capacity),
                     "staff_hour":float(staff_cost),"wait_hour":float(wait_cost),"sla_min":float(sla_min),
                     "sla_target":float(sla_target),"patience_min":float(patience),"priority_share":float(priority),
                     "service_distribution":dist,"service_cv":float(cv),"actions":[],"incident":incident}
            result=evaluate_game(payload)
            visible=configured_units(result["events"][0])
            if visible != int(servers):
                st.error(f"No se guardó: configuraste {int(servers)} {ui['unit_plural']} pero la validación visual produjo {visible}.")
            else:
                st.session_state.pending_payload=payload
                st.session_state.result=result
                st.session_state.frame=0
                st.session_state.sim_status="ready"
                st.session_state.sim_phase="preview"
                st.success("Configuración validada. Revisa el resumen y luego abre la simulación.")
                st.rerun()

        if st.session_state.pending_payload:
            p=st.session_state.pending_payload
            st.markdown('<div class="config-summary-title"><b>Configuración guardada</b><span>Estos datos serán los únicos que gobernarán la simulación.</span></div>',unsafe_allow_html=True)
            metric_cards([
                (ui["unit_plural"].title(),p["staffing"][0],"ok"),
                ("Interarribo",f"{p['arrival_min']:.1f} min","info"),
                ("Servicio",f"{p['service_min']:.1f} min","info"),
                ("Capacidad",p["capacity"],"gold"),
                ("SLA objetivo",f"{p['sla_target']*100:.0f}%","ok"),
                ("Réplicas",p["replications"],"info")
            ],6)
            st.markdown(f"""<div class="config-help"><b>Flujo que se construirá</b>
            <span>{ui['arrival']} → {ui['queue']} → {ui['service']} → {ui['exit']}</span>
            <small>No hay simulación corriendo todavía.</small></div>""",unsafe_allow_html=True)
            o1,o2=st.columns([1.2,3])
            if o1.button("Abrir simulación ▶",type="primary",use_container_width=True,key="open_simulation"):
                st.session_state.sim_screen="simulation"
                st.session_state.sim_phase="preview"
                st.session_state.frame=0
                st.session_state.sim_status="ready"
                st.rerun()
            o2.info("Si cambias cualquier dato arriba, vuelve a guardar antes de abrir la simulación.")
        return

    # ---------------------------
    # PANTALLA B: SIMULACIÓN
    # ---------------------------
    if not st.session_state.pending_payload:
        st.session_state.sim_screen="config";st.session_state.sim_phase="configure";st.rerun()
    if st.session_state.result is None:
        st.session_state.result=evaluate_game(st.session_state.pending_payload)

    result=st.session_state.result
    m=result["metrics"]
    st.caption("Motor: **"+("Central queue_v3" if result.get("engine")=="queue_v3"
               else "Desafíos con reglas avanzadas")+"** · "+result["method"])
    workflow_stepper(st.session_state.sim_phase)

    top_a,top_b=st.columns([1,4])
    if top_a.button("← Volver a configuración",use_container_width=True,key="back_to_config"):
        st.session_state.sim_screen="config"
        st.session_state.sim_phase="preview"
        st.session_state.sim_status="ready"
        st.session_state.frame=0
        st.rerun()
    top_b.markdown(f"""<div class="simulation-lock"><b>Simulación bloqueada a la configuración guardada</b>
    <span>{result['staffing'][0]} {ui['unit_plural']} · llegada {result['config']['arrival_min']:.1f} min · servicio {result['config']['service_min']:.1f} min · capacidad {result['config']['capacity']}</span></div>""",unsafe_allow_html=True)

    # PREVISUALIZACIÓN
    if st.session_state.sim_phase=="preview":
        frame0=result["events"][0]
        stage_title = ("BANCO 3D · THREE.JS · VERSIÓN 2026.10.21" if key=="banco" else "ESCENA CONSTRUIDA · RELOJ EN 0")
        st.markdown(f"""<div class="workflow-head preview"><span>{stage_title}</span><h2>{ui['title']} · verificar antes de iniciar</h2>
        <p>La escena física se generó con los datos guardados. Nada se mueve todavía.</p></div>""",unsafe_allow_html=True)
        if key=="banco":
            st.caption("**VISTA 3D INTERACTIVA** · Ventanillas y sala bancaria en Three.js. Arrastra con el ratón para girar la cámara.")
            components.html(bank_scene_html([frame0],result["config"],preview=True),height=745,scrolling=False)
        else:
            st.markdown(render_sector_scene(key,frame0,"ready"),unsafe_allow_html=True)
        expected=int(result["staffing"][0]);visible=configured_units(frame0)
        metric_cards([
            (ui["service"],f"{visible}/{expected}","ok" if visible==expected else "warn"),
            ("Interarribo",f"{result['config']['arrival_min']:.1f} min","info"),
            ("Servicio",f"{result['config']['service_min']:.1f} min","info"),
            ("Capacidad",result["config"]["capacity"],"gold")
        ],4)
        if visible!=expected:
            st.error("La escena no coincide con la configuración; el inicio queda bloqueado.")
            return
        if st.button("▶ Iniciar simulación desde 0 min",type="primary",use_container_width=True,key="start_from_preview"):
            st.session_state.frame=0
            st.session_state.sim_status="running"
            st.session_state.sim_phase="simulate"
            st.rerun()
        return

    # El Banco usa un único reproductor 3D persistente fuera de fragmentos:
    # el motor Python genera la trayectoria y el navegador anima sus eventos.
    # Evita la recreación del canvas cada 650 ms (parpadeo y desincronización).
    if key=="banco":
        st.caption("**BANCO 3D · THREE.JS · VERSIÓN 2026.10.21** · El motor Python controla todas las llegadas, servicios y movimientos.")
        components.html(bank_scene_html(result["events"],result["config"]),height=745,scrolling=False)
        st.caption("Controles de reproducción, pausa, avance y velocidad integrados en el banco 3D. Los indicadores siguientes son resultados finales de la trayectoria precalculada en Python.")
    else:
        # EJECUCIÓN
        @st.fragment(run_every=0.65)
        def simulation_player():
            result_now=st.session_state.result
            frames=result_now["events"]
            idx=min(st.session_state.frame,len(frames)-1)
            status=st.session_state.sim_status
            if status=="running":
                step=max(1,int(st.session_state.sim_speed))
                if idx < len(frames)-1:
                    idx=min(len(frames)-1,idx+step)
                    st.session_state.frame=idx
                if idx>=len(frames)-1 or frames[idx].get("kind")=="end":
                    st.session_state.sim_status="finished"
                    st.session_state.sim_phase="finished"
                    status="finished"
            frame=frames[idx]
            pct=100*idx/max(1,len(frames)-1)
            active=int(frame.get("active",0));visible=configured_units(frame)

            st.markdown(f"""<div class="ops-shell"><div class="ops-head">
              <div class="ops-title"><span class="ops-icon">{ui['icon']}</span><div><h2>{ui['title']} · simulación dinámica</h2><p>{ui['arrival']} → {ui['queue']} → {ui['service']} → {ui['exit']}</p></div></div>
              <div class="ops-time"><small>Tiempo simulado</small><b>{frame['t']:.1f} min</b><span>{pct:.0f}% de jornada</span></div>
              <div class="ops-mini ok"><small>Completados</small><b>{frame['completed']}</b></div>
              <div class="ops-mini info"><small>En espera</small><b>{frame['queue']}</b></div>
              <div class="ops-mini warn"><small>Rechazados</small><b>{frame['blocked']}</b></div>
            </div><div class="journey-progress"><i style="width:{pct:.1f}%"></i><span class="start-label">INICIO · 0 min</span><span class="end-label">FIN · {int(result_now['config']['duration'])} min</span></div></div>""",unsafe_allow_html=True)

            st.markdown(render_sector_scene(key,frame,status),unsafe_allow_html=True)
            if visible < active:
                st.error(f"Inconsistencia visual: motor={active}, escena={visible}. Se pausó la simulación.")
                st.session_state.sim_status="paused"

            b1,b2,b3,b4,b5,b6=st.columns([1.1,1,1,1,1.1,4])
            if status=="running":
                if b1.button("⏸ Pausa",use_container_width=True,key="sim_pause"):
                    st.session_state.sim_status="paused";st.rerun(scope="fragment")
            elif status=="paused":
                if b1.button("▶ Continuar",type="primary",use_container_width=True,key="sim_continue"):
                    st.session_state.sim_status="running";st.rerun(scope="fragment")
            else:
                b1.button("Finalizado",disabled=True,use_container_width=True,key="sim_done")
            if b2.button("◀ Paso",use_container_width=True,key="sim_prev",disabled=idx==0):
                st.session_state.sim_status="paused";st.session_state.frame=max(0,idx-1);st.rerun(scope="fragment")
            if b3.button("Paso ▶",use_container_width=True,key="sim_next",disabled=idx>=len(frames)-1):
                st.session_state.sim_status="paused";st.session_state.frame=min(len(frames)-1,idx+1);st.rerun(scope="fragment")
            if b4.button("↺ Inicio",use_container_width=True,key="sim_reset"):
                st.session_state.frame=0;st.session_state.sim_status="paused";st.rerun(scope="fragment")
            if b5.button("⏭ Fin",use_container_width=True,key="sim_end",disabled=idx>=len(frames)-1):
                st.session_state.frame=len(frames)-1;st.session_state.sim_status="finished";st.session_state.sim_phase="finished";st.rerun(scope="fragment")
            st.session_state.sim_speed=b6.select_slider("Velocidad",options=[1,2,4,8],value=st.session_state.sim_speed,key="sim_speed_ctl",format_func=lambda x:f"{x}×")
            st.caption(event_text(frame))

        simulation_player()


    # Panel analítico solo dentro de Simulación, nunca en Configuración.
    st.markdown('<div class="section-separator"><b>ANÁLISIS DE LA CORRIDA</b><span>Resultados derivados de los datos guardados.</span></div>',unsafe_allow_html=True)
    left,right=st.columns([1,1.25],gap="medium")
    with left:
        metric_cards([("Wq",f"{m['avg_wait']:.1f} min","info"),("SLA",f"{m['sla']*100:.1f}%","ok"),
                      ("Lq",f"{m['avg_queue']:.2f}","gold"),("ρ",f"{m['utilization']*100:.1f}%","info"),
                      ("Costo",f"S/ {m['total_cost']:.0f}","warn"),("Score",f"{result['score']}/100","gold")],3)
    with right:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=[x["t"] for x in result["series"]],y=[x["queue"] for x in result["series"]],mode="lines",name="Cola",line_shape="hv"))
        fig.add_trace(go.Scatter(x=[x["t"] for x in result["series"]],y=[x["busy"] for x in result["series"]],mode="lines",name="Ocupados",line_shape="hv"))
        fig.update_layout(template="plotly_white",height=260,margin=dict(t=15,l=38,r=10,b=35),xaxis_title="Tiempo (min)",yaxis_title="Cantidad",legend=dict(orientation="h",y=1.12))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    if st.session_state.sim_phase!="finished":
        with st.expander("Intervenir durante la jornada",expanded=False):
            frame=result["events"][min(st.session_state.frame,len(result["events"])-1)]
            i1,i2,i3=st.columns([1,1,2])
            new_servers=i1.number_input(f"Nuevas {ui['unit_plural']}",1,int(cfg["max_servers"]),int(frame["active"]),1,key="intervention_servers")
            minute=i2.number_input("Desde minuto",1,int(result["config"]["duration"])-1,max(1,int(frame["t"])+1),1,key="intervention_minute")
            if i3.button("Aplicar decisión y reiniciar trayectoria",use_container_width=True,key="apply_intervention"):
                actions=[a for a in st.session_state.actions if a["minute"]!=int(minute)]
                actions.append({"minute":int(minute),"servers":int(new_servers)})
                st.session_state.actions=sorted(actions,key=lambda x:x["minute"])
                payload=dict(st.session_state.pending_payload);payload["actions"]=st.session_state.actions
                st.session_state.pending_payload=payload;st.session_state.result=evaluate_game(payload)
                st.session_state.frame=0;st.session_state.sim_status="paused";st.rerun()

    if key=="banco":
        cnew,cdownload=st.columns(2)
        if cnew.button("↺ Nueva corrida · volver a configuración",type="primary",use_container_width=True,key="bank_new_run"):
            st.session_state.sim_screen="config"
            st.session_state.sim_phase="configure"
            st.session_state.pending_payload=None
            st.session_state.result=None
            st.session_state.frame=0
            st.session_state.actions=[]
            st.session_state.sim_status="ready"
            st.rerun()
        cdownload.download_button("Descargar trayectoria y resultados JSON",json.dumps(result,ensure_ascii=False,indent=2),file_name="decision-lab-banco.json",mime="application/json",use_container_width=True,key="bank_json")

    if st.session_state.sim_phase=="finished":
        last=result["events"][-1]
        st.markdown(f"""<div class="finish-card"><div><span>JORNADA FINALIZADA</span><h3>{ui['title']} · evaluación final</h3></div>
        <div class="finish-grid"><div><small>Completados</small><b>{last['completed']}</b></div><div><small>SLA</small><b>{m['sla']*100:.1f}%</b></div><div><small>Costo</small><b>S/ {m['total_cost']:.0f}</b></div><div><small>Score</small><b>{result['score']}/100</b></div></div></div>""",unsafe_allow_html=True)
        f1,f2=st.columns(2)
        if f1.button("Nueva corrida: volver a configuración",type="primary",use_container_width=True,key="new_run"):
            st.session_state.sim_screen="config";st.session_state.sim_phase="configure";st.session_state.pending_payload=None;st.session_state.result=None;st.session_state.frame=0;st.session_state.actions=[];st.session_state.sim_status="ready";st.rerun()
        f2.download_button("Descargar resultado JSON",json.dumps(result,ensure_ascii=False,indent=2),file_name=f"decision-lab-{key}.json",mime="application/json",use_container_width=True)

def model_lab():
    st.header("Modelos matemáticos")
    model=st.selectbox("Modelo",MODELS)
    a,b,c=st.columns(3);arrival=a.number_input("Interarribo (min)",.1,240.0,8.0,.1);service=b.number_input("Servicio (min)",.1,240.0,6.0,.1);servers=c.number_input("Servidores",1,25,2,1)
    try:
        if model in ("M/M/1","M/M/s"):
            r=mms_from_minutes(arrival,service,1 if model=="M/M/1" else int(servers))
        elif model in ("M/M/s/K","M/M/1/c","M/M/s/c"):
            cap=st.number_input("Capacidad total K",int(servers),150,max(int(servers)+5,8),1)
            r=mmsk_from_minutes(arrival,service,1 if model=="M/M/1/c" else int(servers),int(cap))
        elif model=="Erlang B":
            lam,mu=60/arrival,60/service;aoff=lam/mu;bprob=erlang_b(aoff,int(servers));r={"estable":True,"rho":aoff/int(servers),"P_bloqueo":bprob,"P_espera":0,"Lq":0,"Wq":0,"W":service/60,"L":aoff*(1-bprob)}
        elif model=="M/G/1":
            cv=st.number_input("CV servicio",0.0,4.0,1.0,.1);r=mg1_from_minutes(arrival,service,cv)
        else:
            n=st.slider("Clientes",5,100,20);df=pd.DataFrame(dd1_sequence(arrival,service,n));st.dataframe(df,use_container_width=True);st.line_chart(df.set_index("Cliente")["Espera (min)"]);return
        metric_cards([("Estado","Estable" if r.get("estable") else "Inestable","ok" if r.get("estable") else "warn"),("ρ",f"{r.get('rho',0):.3f}","info"),("Lq",f"{r.get('Lq',0):.2f}","info"),("Wq",f"{r.get('Wq',0)*60:.2f} min" if math.isfinite(r.get("Wq",0)) else "∞","info"),("Bloqueo",f"{r.get('P_bloqueo',0)*100:.1f}%","warn")],5)
        st.json(r)
    except ValueError as exc:st.error(str(exc))

def comparator():
    st.header("Comparador de escenarios")
    c1,c2=st.columns(2)
    configs=[]
    for i,col in enumerate((c1,c2),1):
        with col:
            st.subheader(f"Escenario {i}")
            arr=st.number_input("Interarribo",.1,240.0,4.0,key=f"ca{i}");srv=st.number_input("Servicio",.1,240.0,6.0,key=f"cs{i}");s=st.number_input("Servidores",1,20,2+i-1,key=f"cn{i}")
            r=mms_from_minutes(arr,srv,int(s));configs.append((s,r))
    rows=[]
    for i,(s,r) in enumerate(configs,1):rows.append({"Escenario":i,"Servidores":s,"Utilización %":r["rho"]*100,"Wq min":r["Wq"]*60 if r["estable"] else None,"P espera %":r["P_espera"]*100})
    df=pd.DataFrame(rows);st.dataframe(df,use_container_width=True);st.bar_chart(df.set_index("Escenario")["Wq min"])

def economics():
    st.header("Análisis económico")
    c1,c2,c3=st.columns(3);arrival=c1.number_input("Interarribo",.1,240.0,4.0,key="ea");service=c2.number_input("Servicio",.1,240.0,6.0,key="es");maxs=c3.slider("Servidores a evaluar",1,15,8)
    c4,c5,c6=st.columns(3);cs=c4.number_input("Costo servidor/h",0.0,10000.0,20.0);cw=c5.number_input("Costo espera cliente-h",0.0,10000.0,12.0);goal=c6.number_input("Meta Wq min",.1,240.0,5.0)
    rows,rec=recommend_mms_capacity(arrival,service,maxs,cs,cw,goal)
    df=pd.DataFrame(rows);st.dataframe(df,use_container_width=True);st.success(f"Alternativa recomendada: {rec['servers']} servidores · Wq {rec['Wq_min']:.2f} min · costo S/ {rec['cost_total']:.2f}/h")
    st.line_chart(df.set_index("servers")[["cost_staff","cost_wait","cost_total"]])

def network():
    st.header("Red de colas multietapa")
    st.caption("Una sola entidad recorre de 2 a 4 etapas. Los indicadores se consolidan entre "
               "réplicas independientes; la gráfica muestra la primera trayectoria.")
    c1,c2,c3,c4=st.columns(4)
    arrival=c1.number_input("Interarribo medio (min)",.1,240.0,4.0,key="na")
    horizon=c2.number_input("Horizonte (min)",30,1440,480,key="nhorizon")
    reps=c3.number_input("Número de réplicas",1,40,10,key="nreps")
    seed=c4.number_input("Semilla de simulación",1,999999999,2026,key="nseed")
    count=st.slider("Etapas",2,4,3)
    stages=[]
    defaults=[("Recepción",5,2),("Atención",8,3),("Pago",4,2),("Entrega",6,2)]
    for i in range(count):
        a,b,c=st.columns([1.2,1,1])
        name=a.text_input("Nombre de etapa",defaults[i][0],key=f"nn{i}")
        sm=b.number_input("Servicio medio (min)",.1,240.0,float(defaults[i][1]),key=f"ns{i}")
        sv=c.number_input("Servidores en etapa",1,20,int(defaults[i][2]),key=f"nv{i}")
        stages.append({"name":name,"service_min":sm,"servers":sv})
    if st.button("Simular red",type="primary"):
        try:
            result=evaluate_network({"arrival_min":arrival,"horizon":horizon,
                "replications":int(reps),"seed":int(seed),"stages":stages})
        except (ValueError,RuntimeError) as exc:
            st.error(f"Configuración de red inválida: {exc}")
        else:
            st.session_state.network_result=result
    if "network_result" not in st.session_state:
        st.info("Configura la red y pulsa Simular red para ver el flujo y las estadísticas.")
        return
    r=st.session_state.network_result
    m=r["metrics"]
    metric_cards([("Llegadas (promedio)",f"{m['arrivals']:.1f}","info"),
                  ("Completados (promedio)",f"{m['completed']:.1f}","ok"),
                  ("Throughput",f"{m['throughput_rate']:.2f}/h","info"),
                  ("Tiempo sistema",f"{m['avg_system']:.1f} min","gold")],4)
    st.caption(f"Modelo: {r['model']} · Motor: {r['engine']} · "
               f"{r['replications_effective']} réplicas · Horizonte {r['horizon']} min.")
    st.subheader("Conservación de flujo por etapa")
    df=pd.DataFrame(r["stages"])
    columns=["name","servers","arrived","completed","in_stage_at_close",
             "waiting_at_close","in_service_at_close","avg_queue","avg_wait","utilization"]
    st.dataframe(df[columns],hide_index=True,use_container_width=True)
    critical=r["stages"][r["bottleneck_index"]]
    st.info(f"Etapa con mayor utilización media: **{critical['name']}**, "
            f"{critical['utilization']*100:.1f}%. "
            "Es una alerta exploratoria de capacidad, no una demostración causal.")
    st.subheader("Colas por etapa · Primera réplica")
    fig=go.Figure()
    for i,stage in enumerate(r["stages"]):
        fig.add_trace(go.Scatter(x=[f["t"] for f in r["frames"]],
            y=[f["queues"][i] for f in r["frames"]],
            mode="lines",name=stage["name"],line_shape="hv"))
    st.plotly_chart(fig,use_container_width=True)
    if r["replications_effective"]>1:
        st.subheader("Réplicas y precisión estadística")
        st.dataframe(pd.DataFrame(r["runs"]),hide_index=True,use_container_width=True)
        st.dataframe(pd.DataFrame(r["confidence_95"]).T,use_container_width=True)
        st.caption("IC exploratorios normales de 95%; no representan precisión garantizada.")
    st.download_button("Descargar resultados de red JSON",
        json.dumps(r,ensure_ascii=False,indent=2),
        file_name="astalanka-opt-red-colas.json",mime="application/json")

def reports():
    st.header("Reportes y progreso")
    metric_cards([("Nivel",st.session_state.level,"gold"),("XP",st.session_state.xp,"info"),("Monedas",st.session_state.coins,"gold")],3)
    if st.session_state.score_history:
        df=pd.DataFrame([{"Escenario":x["scenario"],"Score":x["score"],"Costo":x["metrics"]["total_cost"],"SLA":x["metrics"]["sla"]} for x in st.session_state.score_history])
        st.dataframe(df,use_container_width=True)
        st.download_button("Descargar historial CSV",df.to_csv(index=False).encode(),file_name="decision-lab-historial.csv",mime="text/csv")
    else:st.info("Todavía no hay partidas en esta sesión.")
    st.caption("En Streamlit Community Cloud el estado de sesión no es una base de datos persistente. La persistencia multiusuario completa permanece en la versión Django/PostgreSQL.")

def analytics_hub():
    """Análisis central; herramientas antiguas protegidas hasta migrar su motor."""
    from report_v3 import report_pdf, report_xlsx

    st.header("Análisis y reportes")
    st.caption("Compara experimentos realmente ejecutados con sus parámetros y procedencia. "
               "Los registros se conservan solo durante esta sesión de Streamlit.")
    mode=st.radio("Espacio de análisis",
                  ["Comparar corridas","Informe del simulador","Herramientas clásicas","Historial de desafíos"],
                  horizontal=True,key="analysis_workspace")
    runs=st.session_state.get("v3_registry",[])
    if mode=="Comparar corridas":
        if not runs:
            st.info("Todavía no hay experimentos. Entra a Simulador 3D, guarda y valida una configuración; "
                    "la corrida aparecerá aquí automáticamente.")
            return
        st.dataframe(pd.DataFrame(comparison_rows(runs)),use_container_width=True,hide_index=True)
        by_id={r["id"]:r for r in runs}
        choices=st.multiselect("Corridas a comparar",list(by_id),
                               default=list(by_id)[-2:],
                               format_func=lambda key: f"{key} · {by_id[key]['sector']} · "
                               f"{by_id[key]['model']} · {by_id[key]['horizon_min']} min",
                               key="comparison_runs")
        selected=[by_id[k] for k in choices]
        if len(selected)>=2:
            table=pd.DataFrame(comparison_rows(selected)).set_index("ID")
            st.bar_chart(table[["Wq (min)","Lq (clientes)"]])
            st.bar_chart(table[["SLA (%)","Utilización (%)"]])
            decision=recommend_comparison(selected)
            if not decision["valid"]:
                st.warning(decision["reason"])
            elif decision["recommended"] is None:
                st.warning(f"Ninguna corrida supera el SLA objetivo de {decision['target']*100:.1f}% "
                           "bajo los supuestos comunes. No hay recomendación factible.")
            else:
                st.info(decision["reason"])
                st.success(f"**Menor costo con SLA cumplido:** {decision['recommended']} · "
                           f"S/ {decision['cost']:,.2f} · SLA {decision['sla']*100:.1f}% "
                           f"(meta: {decision['target']*100:.1f}%).")
                st.caption(decision["caveat"])
        csv=pd.DataFrame(comparison_rows(runs)).to_csv(index=False).encode("utf-8-sig")
        st.download_button("Descargar comparación CSV",csv,
                           file_name="astalanka-opt-comparacion.csv",mime="text/csv")
        st.download_button("Descargar registro JSON",
                           json.dumps(runs,ensure_ascii=False,indent=2),
                           file_name="astalanka-opt-experimentos.json",mime="application/json")
        try:
            report_bytes=comparison_xlsx(selected if selected else runs)
        except (ValueError,KeyError) as exc:
            st.error(f"No se pudo crear el Excel comparativo: {exc}")
        else:
            st.download_button("Comparación Excel con trazabilidad",report_bytes,
                file_name="astalanka-opt-comparacion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif mode=="Informe del simulador":
        result=st.session_state.get("v3_result")
        if result is None:
            st.info("Ejecuta primero una corrida desde Simulador 3D.")
            return
        st.write(f"**Modelo:** {result['model']} · **Modalidad:** {result['mode']} · "
                 f"**Horizonte:** {result['horizon']} minutos")
        st.dataframe(pd.DataFrame(result["metrics"].items(),columns=["Indicador","Resultado"]),
                     hide_index=True,use_container_width=True)
        st.caption("Las medidas son consolidadas por réplica; no deben confundirse con la animación de una sola corrida.")
        left,right=st.columns(2)
        try:
            data_pdf=report_pdf(result,st.session_state.get("v3_optimization"),
                                st.session_state.get("v3_optimization_dynamic"))
            data_xlsx=report_xlsx(result,st.session_state.get("v3_optimization"),
                                  st.session_state.get("v3_optimization_dynamic"))
        except Exception as exc:
            st.error(f"El reporte no pudo generarse: {exc}")
            return
        left.download_button("Informe gerencial PDF",data_pdf,mime="application/pdf",
                             file_name="astalanka-opt-informe.pdf",use_container_width=True)
        right.download_button("Reporte técnico Excel",data_xlsx,
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                              file_name="astalanka-opt-analisis.xlsx",use_container_width=True)
    elif mode=="Herramientas clásicas":
        st.warning("Funciones de la versión anterior, disponibles durante la migración. "
                   "Sus resultados son estacionarios M/M/s o auxiliares y NO se consideran "
                   "corridas del motor central; no se mezclan automáticamente con la comparación.")
        tool=st.selectbox("Herramienta heredada",["Modelos teóricos","Comparador M/M/s",
                                                  "Análisis económico M/M/s"])
        if tool=="Modelos teóricos":
            model_lab()
        elif tool=="Comparador M/M/s":
            comparator()
        else:
            economics()
    else:
        reports()

def home():
    run_decision_lab_v3()

css();init_state();topbar();section=sidebar()
if section=="Simulador 3D":
    run_decision_lab_v3()
elif section=="Desafíos gerenciales":
    st.caption("Los desafíos mantienen actualmente el motor de incidentes y puntuación de la "
               "versión anterior; su integración plena al contrato multimodelo es el hito H2.")
    run_challenge_ui()
elif section=="Red de colas":
    st.caption("Red multietapa H3: seguimiento de flujo por etapa, réplicas independientes y "
               "contrato analítico v3. El motor de red conserva su simulación tándem especializada.")
    network()
else:
    analytics_hub()
