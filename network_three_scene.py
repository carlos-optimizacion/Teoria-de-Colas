"""Visualizador tridimensional de redes tándem, alimentado por eventos Python.

El navegador solo posiciona entidades y reproduce instantáneas; no genera
tiempos de llegada, atención, transferencias ni métricas.
"""
from __future__ import annotations
import json


def network_scene_html(result: dict, *, preview: bool = False) -> str:
    stages = result.get("stages", [])
    frames = result.get("frames", [])
    if not 2 <= len(stages) <= 10 or not frames:
        raise ValueError("La escena 3D necesita de 2 a 10 etapas y al menos un fotograma")
    if any(len(f.get("queues", [])) != len(stages) or
           len(f.get("busy", [])) != len(stages) or
           len(f.get("queue_ids", [])) != len(stages) or
           len(f.get("service_ids", [])) != len(stages) for f in frames):
        raise ValueError("La trayectoria debe aportar estados físicos por etapa")
    payload = {
        "stages": [{
            "name": str(s["name"]), "servers": int(s["servers"]),
            "service_min": float(s["service_min"]),
            "avg_wait": float(s["avg_wait"]),
            "avg_queue": float(s["avg_queue"]),
            "utilization": float(s["utilization"]),
        } for s in stages],
        "frames": frames[:1] if preview else frames,
        "horizon": float(result["horizon"]),
        "preview": bool(preview),
        "frame_stride": int(result.get("frame_sample_stride", 1)),
        "bottleneck": int(result.get("bottleneck_index", -1)),
    }
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return HTML.replace("/*__NETWORK_PAYLOAD__*/", "const payload=" + data + ";")


HTML = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.166.1/build/three.module.js",
"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.166.1/examples/jsm/"}}
</script>
<style>
*{box-sizing:border-box}html,body{margin:0;height:100%;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;color:#153e5a;background:#e9f2f6}
.app{height:100vh;min-height:650px;display:flex;flex-direction:column;border:1px solid #c9dfe9;overflow:hidden;border-radius:16px;background:white}
.head{padding:12px 16px;background:#103652;color:white;display:flex;justify-content:space-between;gap:12px;align-items:center}
.head strong{font-size:16px}.head small{display:block;color:#c0dfe9;font-size:11px;margin-top:4px}
.pill{font-size:11px;background:#ffffff20;border:1px solid #ffffff30;border-radius:20px;padding:7px 10px;white-space:nowrap}
.global{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;background:#f2f8fb;padding:10px}
.metric{border:1px solid #d7e6ec;background:white;border-radius:10px;padding:8px 12px}.metric small{display:block;color:#698598;font-size:10px}.metric b{display:block;font-size:18px}
.view{position:relative;flex:1;min-height:270px;background:radial-gradient(ellipse at 50% 20%,#e0f3fb 0%,#ccdae4 100%);overflow:hidden}
canvas{width:100%;height:100%;display:block;touch-action:none}
.overlay{position:absolute;left:12px;top:12px;background:#123e5ddc;color:white;padding:8px 10px;border-radius:9px;font-size:11px;pointer-events:none;max-width:80%}
.loading{position:absolute;inset:0;display:grid;place-items:center;background:#e9f5fa;z-index:5;text-align:center;padding:22px}
.nodes{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px;padding:8px;background:#f4f9fb;max-height:215px;overflow:auto}
.node{border:1px solid #d4e2e8;border-top:4px solid #2e9d82;background:white;border-radius:8px;padding:6px 9px;min-width:0}
.node.active{background:#edf8fb;outline:1px solid #2a8eb8}
.node.warn{border-top-color:#f09a41}.node.bad{border-top-color:#ce6450}
.node h4{font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin:0 0 4px}
.node .values{font-size:10px;color:#5c7888;display:grid;grid-template-columns:repeat(2,1fr);gap:2px}
.node .values b{color:#184867;font-variant-numeric:tabular-nums}
.player{border-top:1px solid #d7e7ef;display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:center;padding:10px}
.player button,.player select{background:#eaf4fa;color:#174c6b;border:1px solid #c8dae6;border-radius:7px;padding:7px 11px;cursor:pointer;font-weight:700;font-size:12px}
.player .primary{background:#167eae;color:white}
.player input{width:100%;accent-color:#167eae}
.legend{display:flex;flex-wrap:wrap;gap:12px;font-size:10px;color:#678497;padding:4px 12px 8px;background:white}
.legend span:before{content:"";display:inline-block;border-radius:50%;height:8px;width:8px;background:#2e9d82;margin-right:5px}
.legend span:nth-child(2):before{background:#eea24b}.legend span:nth-child(3):before{background:#cf6652}
@media(max-width:750px){.nodes{grid-template-columns:repeat(2,minmax(0,1fr));max-height:280px}.global{grid-template-columns:repeat(2,1fr)}.player{grid-template-columns:1fr}.head{align-items:flex-start;flex-direction:column}.app{min-height:720px}}
</style></head><body><div class="app">
<header class="head"><div><strong>ASTALANKA OPT · RED DE COLAS 3D</strong><small>Red tándem de procesos · geometría sincronizada con el motor Python</small></div>
<span class="pill" id="summary">Preparando…</span></header>
<div class="global">
<div class="metric"><small>Minuto simulado</small><b id="time">0.0</b></div>
<div class="metric"><small>En espera · toda la red</small><b id="waiting">0</b></div>
<div class="metric"><small>En atención · toda la red</small><b id="busy">0</b></div>
<div class="metric"><small>Salidas acumuladas</small><b id="done">0</b></div>
</div>
<div class="view" id="stage">
<div class="loading" id="loading">Preparando representación tridimensional de la red…</div>
<div class="overlay">Arrastra para girar · Rueda para acercar · Las personas y ocupaciones provienen de Python</div>
</div>
<div id="nodes" class="nodes"></div>
<div class="player">
<div><button id="play" class="primary">▶ Reproducir</button><button id="reset">↺ Inicio</button></div>
<input type="range" id="seek" min="0" max="0" step="1" value="0" aria-label="Instante de simulación"/>
<div><select id="speed" aria-label="Velocidad"><option value="2">2×</option><option value="6" selected>6×</option><option value="15">15×</option><option value="30">30×</option></select></div>
</div>
<div class="legend"><span>Servicio normal</span><span>Congestión media</span><span>Congestión alta</span><span>Se muestran hasta 10 entidades por cola; los contadores incluyen el total real.</span></div>
</div>
<script type="module">
import * as THREE from "three";
import {OrbitControls} from "three/addons/controls/OrbitControls.js";
/*__NETWORK_PAYLOAD__*/
const byId=(x)=>document.getElementById(x);
const stages=payload.stages, frames=payload.frames,n=stages.length;
const scene=new THREE.Scene();scene.background=new THREE.Color(0xd4e8f1);
const camera=new THREE.PerspectiveCamera(42,1,.1,220);
camera.position.set(0,n>5?24:18,n>5?24:20);camera.lookAt(0,0,0);
// Acercamiento inicial adaptativo: con pocas etapas, utilizar el lienzo disponible.
camera.zoom=n<=3?1.65:n<=5?1.35:1.0;camera.updateProjectionMatrix();
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.5));
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
byId("stage").appendChild(renderer.domElement);
const orbit=new OrbitControls(camera,renderer.domElement);
orbit.enableDamping=true;orbit.maxPolarAngle=Math.PI/2.06;
orbit.target.set(0,0,0);orbit.minDistance=8;orbit.maxDistance=65;
scene.add(new THREE.HemisphereLight(0xffffff,0x7d99aa,2.5));
const keyLight=new THREE.DirectionalLight(0xffffff,2.3);keyLight.position.set(-8,21,12);
keyLight.castShadow=true;keyLight.shadow.mapSize.set(2048,2048);scene.add(keyLight);
const material=(c)=>new THREE.MeshStandardMaterial({color:c,roughness:.76,metalness:.04});
const floor=material(0xeaf2f5),navy=material(0x1b4e69),metal=material(0x9db6c2),
green=material(0x36a889),amber=material(0xe9a34c),red=material(0xd86753);
function box(w,h,d,mat,x,y,z,parent=scene){
 const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);
 m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;
}
function textSprite(text,width=3.5,color="#143e58"){
 const can=document.createElement("canvas");can.width=640;can.height=100;
 const ctx=can.getContext("2d");ctx.fillStyle="#ffffff";ctx.fillRect(0,0,640,100);
 ctx.fillStyle=color;ctx.font="bold 35px system-ui,sans-serif";
 const txt=String(text);
 let label=txt;while(ctx.measureText(label).width>580&&label.length>2)label=label.slice(0,-2)+"…";
 ctx.fillText(label,26,65);
 const t=new THREE.CanvasTexture(can);t.colorSpace=THREE.SRGBColorSpace;
 const p=new THREE.Mesh(new THREE.PlaneGeometry(width,.55),
 new THREE.MeshBasicMaterial({map:t,transparent:true,side:THREE.DoubleSide}));
 p.rotation.x=-.15;return p;
}
const cols=Math.min(5,n);
const positions=stages.map((st,i)=>{
 if(n<=5)return {x:(i-(n-1)/2)*4.1,z:0};
 const row=Math.floor(i/5),col=i%5;
 return{x:((row===0?col:4-col)-2)*4.1,z:row===0?-3.6:4.0};
});
box(23,.24,n>5?15:10,floor,0,-.15,0);
for(let i=0;i<n;i++){
 const p=positions[i];const node=new THREE.Group();node.position.set(p.x,0,p.z);scene.add(node);
 box(3.5,.06,3.15,material(0xc1dee7),0,.015,0,node);
 box(2.5,.78,.70,navy,0,.39,-.73,node);
 box(2.55,.10,.85,metal,0,.79,-.73,node);
 for(let slot=0;slot<Math.min(stages[i].servers,20);slot++){
   const x=((slot%5)-Math.min(4,stages[i].servers-1)/2)*.45;
   const z=-.12+Math.floor(slot/5)*.4;
   box(.26,.16,.26,material(0x7aafbe),x,.10,z,node);
 }
 const plate=textSprite((i+1)+" · "+stages[i].name,3.35);
 plate.position.set(0,1.75,-1.45);node.add(plate);
 const post=box(.16,1.6,.16,navy,-1.64,.84,-1.46,node);
 const lamp=box(.52,.19,.34,green,1.40,1.60,-1.22,node);
 node.userData.lamp=lamp;
}
for(let i=0;i<n-1;i++){
 const a=positions[i],b=positions[i+1];
 const points=[new THREE.Vector3(a.x,.08,a.z),new THREE.Vector3(b.x,.08,b.z)];
 const path=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),
 new THREE.LineBasicMaterial({color:0x2897b4}));
 scene.add(path);
 const arrow=new THREE.ArrowHelper(new THREE.Vector3(b.x-a.x,0,b.z-a.z).normalize(),
   new THREE.Vector3((a.x+b.x)/2,.10,(a.z+b.z)/2),.82,0x258aaa,.37,.22);
 scene.add(arrow);
}
const unit=(color)=>{
 const group=new THREE.Group();
 const head=new THREE.Mesh(new THREE.SphereGeometry(.17,10,8),material(0xe8b88e));head.position.y=.93;group.add(head);
 box(.32,.43,.25,material(color),0,.54,0,group);
 for(const x of [-.11,.11])box(.10,.33,.10,navy,x,.19,0,group);
 return group;
};
const actors=new Map();
function positionOf(stageIndex,type,idx){
 const p=positions[stageIndex];
 if(type==="busy"){
   const k=Math.min(idx,19),len=Math.min(stages[stageIndex].servers,20);
   return new THREE.Vector3(p.x+((k%5)-Math.min(4,len-1)/2)*.45,0,
      p.z-.05+Math.floor(k/5)*.40);
 }
 const col=idx%5,row=Math.floor(idx/5);
 return new THREE.Vector3(p.x+(col-2)*.55,0,p.z+1.18+row*.48);
}
function applyFrame(i){
 const f=frames[i];byId("time").textContent=Number(f.t).toFixed(1)+" min";
 byId("waiting").textContent=f.queues.reduce((a,b)=>a+b,0);
 byId("busy").textContent=f.busy.reduce((a,b)=>a+b,0);
 byId("done").textContent=f.completed;
 byId("seek").value=i;
 const visible=new Set();
 for(let j=0;j<n;j++){
   const ids=(f.queue_ids[j]||[]),service=(f.service_ids[j]||[]);
   const occ=Number(f.busy[j]),q=Number(f.queues[j]);
   const hot=occ/stages[j].servers>=.85 && q>0;
   const med=q>0;const tile=byId("node-"+j);
   tile.className="node"+(hot?" bad":med?" warn":"")+(j===payload.bottleneck?" active":"");
   tile.querySelector(".q").textContent=q;
   tile.querySelector(".b").textContent=occ+"/"+stages[j].servers;
   tile.querySelector(".in").textContent=(f.arrived_stage||[])[j]??0;
   tile.querySelector(".out").textContent=(f.completed_stage||[])[j]??0;
   tile.querySelector(".w").textContent=Number((f.avg_wait_stage||[])[j]??0).toFixed(1)+" min";
   tile.querySelector(".rho").textContent=(100*Number((f.utilization_stage||[])[j]??0)).toFixed(1)+"%";
   for(let k=0;k<ids.length;k++){
     const id=String(ids[k]),key="client-"+id;visible.add(key);
     if(!actors.has(key)){const a=unit(0x3c93bc);scene.add(a);actors.set(key,a);a.position.copy(positionOf(j,"queue",k));}
     actors.get(key).userData.destination=positionOf(j,"queue",k);
   }
   for(let k=0;k<service.length;k++){
     const cid=service[k];if(cid==null)continue;
     const key="client-"+String(cid);visible.add(key);
     if(!actors.has(key)){const a=unit(0x349e88);scene.add(a);actors.set(key,a);a.position.copy(positionOf(j,"busy",k));}
     actors.get(key).userData.destination=positionOf(j,"busy",k);
   }
 }
 for(const [id,actor] of actors)if(!visible.has(id)){scene.remove(actor);actors.delete(id);}
}
byId("summary").textContent=stages.length+" etapas · "+payload.horizon+" min · "+
  (payload.preview?"Vista previa estática":"Fotogramas del motor Python");
byId("nodes").innerHTML=stages.map((s,i)=>
  '<div class="node" id="node-'+i+'" title="'+(i===payload.bottleneck?"Mayor utilización media":"Etapa de servicio")+'">'+
  '<h4>'+(i+1)+'. '+s.name.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;")+'</h4>'+
  '<div class="values"><span>Cola <b class="q">0</b></span><span>Ocupados <b class="b">0</b></span>'+
  '<span>Entradas <b class="in">0</b></span><span>Salidas <b class="out">0</b></span>'+
  '<span>Espera <b class="w">0</b></span><span>ρ(t) <b class="rho">0%</b></span></div></div>').join("");
byId("seek").max=Math.max(0,frames.length-1);
let idx=0,running=false,lastStep=0;
function select(i){idx=Math.max(0,Math.min(frames.length-1,Math.round(i)));applyFrame(idx);
 if(idx>=frames.length-1){running=false;byId("play").textContent="▶ Reproducir";}}
byId("play").disabled=payload.preview||frames.length<2;
byId("play").addEventListener("click",()=>{
 running=!running;byId("play").textContent=running?"⏸ Pausar":"▶ Reproducir";lastStep=performance.now();
 if(idx>=frames.length-1){select(0);running=true;byId("play").textContent="⏸ Pausar";}
});
byId("reset").addEventListener("click",()=>{running=false;select(0);byId("play").textContent="▶ Reproducir";});
byId("seek").addEventListener("input",e=>{running=false;select(Number(e.target.value));byId("play").textContent="▶ Reproducir";});
function resize(){const view=byId("stage"),w=view.clientWidth,h=view.clientHeight;
 renderer.setSize(w,h,false);camera.aspect=w/Math.max(h,1);camera.updateProjectionMatrix();}
new ResizeObserver(resize).observe(byId("stage"));resize();applyFrame(0);
byId("loading").remove();
function loop(now){
 requestAnimationFrame(loop);orbit.update();
 if(running && now-lastStep>1000/Number(byId("speed").value)){
   select(idx+1);lastStep=now;
 }
 for(const a of actors.values())if(a.userData.destination)
   a.position.lerp(a.userData.destination,.13);
 renderer.render(scene,camera);
}
requestAnimationFrame(loop);
byId("stage").dataset.nodes=String(n);
byId("stage").dataset.source="python-network-events";
byId("stage").dataset.preview=String(payload.preview);
</script></body></html>
"""
