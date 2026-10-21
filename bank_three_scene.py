"""Banco 3D: reproductor Three.js basado exclusivamente en eventos del motor Python.

La vista NO calcula llegadas, servicios ni resultados: reproduce las trazas
generadas por evaluate_game. La configuración se guarda previamente en Streamlit.
"""
from __future__ import annotations

import json


def bank_scene_html(events: list[dict], config: dict, *, preview: bool = False) -> str:
    """Build a self-contained HTML component for Streamlit's iframe.

    All statistical simulation comes from Python. The browser interpolates
    geometry between event snapshots; it never invents clients or stations.
    """
    if not events:
        raise ValueError("La escena bancaria necesita al menos un evento")
    initial = events[0]
    if int(initial.get("active", 0)) < 1:
        raise ValueError("La corrida debe configurar al menos una ventanilla")
    data = {
        "frames": [initial] if preview else events,
        "preview": bool(preview),
        "config": {
            "arrival_min": config.get("arrival_min", 0),
            "service_min": config.get("service_min", 0),
            "capacity": config.get("capacity", 0),
            "duration": config.get("duration", 0),
            "servers": int(initial["active"]),
        },
    }
    # Prevent a JSON value ever closing the enclosing script tag.
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return BANK_HTML.replace("/*__PAYLOAD__*/", "const payload = " + payload + ";")


BANK_HTML = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.166.1/build/three.module.js",
"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.166.1/examples/jsm/"}}
</script>
<style>
*{box-sizing:border-box}html,body{margin:0;height:100%;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;color:#153750;background:#e7f0f6}
.bank3d{height:100vh;min-height:560px;display:flex;flex-direction:column;overflow:hidden;border:1px solid #cbdfe9;border-radius:16px;background:#eef5f8}
.header{background:#103858;color:#fff;display:flex;justify-content:space-between;align-items:center;padding:12px 17px;gap:12px}
.brand{display:flex;align-items:center;gap:11px}.brand-mark{display:grid;place-items:center;border-radius:12px;background:#2e8cb5;border:1px solid #ffffff55;font-size:23px;width:45px;height:45px}.brand b{display:block;letter-spacing:.035em;font-size:15px}.brand small{color:#bedce8;display:block;font-size:11px;margin-top:3px}
.config{display:flex;flex-wrap:wrap;gap:7px;justify-content:flex-end}.config span{font-size:11px;background:#ffffff16;border:1px solid #ffffff2e;padding:6px 10px;border-radius:20px;white-space:nowrap}
.stats{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;padding:10px 13px;background:#f5fafc;border-bottom:1px solid #d7e5ed}
.kpi{background:#fff;border:1px solid #deebf0;border-radius:11px;padding:8px 11px;min-width:0}.kpi small{font-size:10px;display:block;color:#647f90;white-space:nowrap}.kpi b{font-size:21px;color:#173f60;font-variant-numeric:tabular-nums;line-height:1.2}.kpi.time b{font-size:19px}.kpi.warn b{color:#bb683d}
.stage{position:relative;flex:1;min-height:280px;background:radial-gradient(ellipse at 45% 30%,#cbe8f5 0%,#d7e5ec 65%,#afc8d5 100%);overflow:hidden}
canvas{display:block;width:100%;height:100%;touch-action:none}
.stage-hint{position:absolute;top:14px;left:14px;padding:8px 11px;border-radius:10px;background:#103858dc;color:white;font-size:11px;pointer-events:none}
.zone-labels{position:absolute;bottom:12px;left:12px;right:12px;display:flex;gap:7px;flex-wrap:wrap;pointer-events:none}
.zone-labels span{font-size:10px;color:#25495d;border:1px solid #cfe1e7;background:#fffffff2;box-shadow:0 3px 11px #1c567326;border-radius:8px;padding:6px 10px}
.loading{position:absolute;inset:0;display:grid;place-items:center;text-align:center;background:#e6f3f9;color:#205876;padding:20px;font-size:13px;z-index:3}
.player{background:#fff;border-top:1px solid #d9e8ee;padding:9px 13px 12px;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:11px}
.controls{display:flex;gap:5px;flex-wrap:wrap}.controls button,.controls select{background:#eef6fa;color:#194b67;border:1px solid #cbdfe9;padding:8px 10px;border-radius:8px;font-weight:750;cursor:pointer;font-size:12px}.controls button.main{background:#1379ad;color:#fff;border-color:#1379ad}.controls button:disabled{opacity:.4;cursor:not-allowed}
.seek{min-width:0}.seek input{width:100%;accent-color:#147fae;cursor:pointer}.seek-labels{display:flex;justify-content:space-between;color:#7390a1;font-size:10px}
.state{font-size:11px;font-weight:800;white-space:nowrap;color:#146d91}.state.ready{color:#8d6b18}.state.finished{color:#287c55}
.footer{display:flex;justify-content:space-between;gap:7px;padding:5px 15px 9px;font-size:10px;color:#5e7e91;background:#fff}
@media(max-width:800px){.header{align-items:flex-start;flex-direction:column}.config{justify-content:flex-start}.stats{grid-template-columns:repeat(3,1fr)}.player{grid-template-columns:1fr;gap:7px}.stage-hint{font-size:10px}.footer{display:block}.bank3d{min-height:650px}.kpi b{font-size:18px}}
</style>
</head>
<body>
<div class="bank3d">
 <div class="header">
  <div class="brand"><span class="brand-mark">🏦</span><div><b>DECISION LAB · BANCO 3D</b><small>Agencia bancaria · simulación de eventos discretos</small></div></div>
  <div class="config" id="config"></div>
 </div>
 <div class="stats">
  <div class="kpi time"><small>Tiempo simulado</small><b id="stat-time">0.0 min</b></div>
  <div class="kpi"><small>Ventanillas activas</small><b id="stat-active">0</b></div>
  <div class="kpi"><small>Clientes esperando</small><b id="stat-queue">0</b></div>
  <div class="kpi"><small>Atendidos</small><b id="stat-served">0</b></div>
  <div class="kpi warn"><small>Rechazados / abandonos</small><b id="stat-lost">0</b></div>
 </div>
 <div class="stage" id="stage">
  <div id="loading" class="loading">Preparando agencia bancaria 3D…</div>
  <div class="stage-hint">Arrastra para girar · Rueda para acercar · La posición y ocupación provienen de la simulación Python</div>
  <div class="zone-labels"><span>01 · Ingreso / turnero</span><span>02 · Sala de espera</span><span>03 · Ventanillas de atención</span><span>04 · Salida</span></div>
 </div>
 <div class="player">
  <div class="controls">
   <button class="main" id="play">▶ Iniciar</button>
   <button id="back" title="Evento anterior">◀ Evento</button>
   <button id="next" title="Evento siguiente">Evento ▶</button>
   <button id="reset">↺ Inicio</button>
   <select id="speed" aria-label="Velocidad de reproducción"><option value="1">1×</option><option value="2">2×</option><option value="4">4×</option><option value="8">8×</option></select>
  </div>
  <div class="seek"><input id="seek" type="range" min="0" max="0" value="0" aria-label="Elegir evento"><div class="seek-labels"><span id="event-count">Evento 0 / 0</span><span id="event-kind">Preparado</span></div></div>
  <span id="state" class="state ready">ESCENA LISTA</span>
 </div>
 <div class="footer"><span>Modelo M/M/s/K y distribuciones configuradas en el motor Python. Reproducción acelerada por eventos.</span><span id="visual-limit"></span></div>
</div>
<script type="module">
/*__PAYLOAD__*/
const frames=payload.frames, cfg=payload.config, preview=payload.preview;
const $=id=>document.getElementById(id);
$('config').innerHTML='<span>Ventanillas: <b>'+cfg.servers+'</b></span><span>Interarribo: <b>'+Number(cfg.arrival_min).toFixed(1)+' min</b></span><span>Servicio: <b>'+Number(cfg.service_min).toFixed(1)+' min</b></span><span>Capacidad total: <b>'+cfg.capacity+'</b></span>';
let idx=0,playing=false,speed=1,accumulator=0,last=0;
const maxVisibleClients=42;
$('seek').max=Math.max(0,frames.length-1);
if(preview){$('play').disabled=true;$('state').textContent='PREVISUALIZACIÓN · SIN MOVIMIENTO';}
window.addEventListener('unhandledrejection',()=>{$('loading').textContent='No se pudo cargar Three.js. Comprueba el acceso a cdn.jsdelivr.net.';});
try{
 const THREE=await import('three');
 const addon=await import('three/addons/controls/OrbitControls.js');
 const OrbitControls=addon.OrbitControls;
 const stage=$('stage'),scene=new THREE.Scene();
 scene.background=new THREE.Color(0xddeaf1);
 const camera=new THREE.PerspectiveCamera(42,1,0.1,200);
 camera.position.set(15.5,16.5,19);
 const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});
 renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.6));
 renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
 renderer.outputColorSpace=THREE.SRGBColorSpace;
 renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.4;
 stage.insertBefore(renderer.domElement,stage.firstChild);
 const controls=new OrbitControls(camera,renderer.domElement);
 controls.target.set(0,0,-.45);controls.enableDamping=true;controls.dampingFactor=.06;controls.enablePan=false;
 controls.minDistance=13;controls.maxDistance=36;controls.minPolarAngle=.25;controls.maxPolarAngle=1.48;controls.update();
 scene.add(new THREE.HemisphereLight(0xeaf8ff,0x9fbbca,2.0));
 const sun=new THREE.DirectionalLight(0xfff6e8,2.7);sun.position.set(6,15,9);sun.castShadow=true;
 sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-16;sun.shadow.camera.right=16;
 sun.shadow.camera.top=16;sun.shadow.camera.bottom=-16;sun.shadow.normalBias=.035;scene.add(sun);
 const mat=(color,other={})=>new THREE.MeshStandardMaterial(Object.assign({color,roughness:.72,metalness:.06},other));
 const navy=mat(0x194966),blue=mat(0x267da5),cream=mat(0xf8f8f2),glass=mat(0x83d5f2,{transparent:true,opacity:.29,roughness:.1,metalness:.05,depthWrite:false});
 const tile=mat(0xe7edf0),gold=mat(0xd5a95b,{metalness:.4,roughness:.3}),wood=mat(0xb67d53),steel=mat(0x7b91a1,{metalness:.45,roughness:.32});
 const add=(g,m,p=[0,0,0],parent=scene)=>{const o=new THREE.Mesh(g,m);o.position.set(...p);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o};
 const box=(w,h,d,m,p,parent)=>add(new THREE.BoxGeometry(w,h,d),m,p,parent);
 const cyl=(r1,r2,h,m,p,parent)=>add(new THREE.CylinderGeometry(r1,r2,h,12),m,p,parent);
 const sphere=(r,m,p,parent)=>add(new THREE.SphereGeometry(r,16,12),m,p,parent);
 const label=(text,w,h,color=0x173f61,fontSize=54)=>{
   const can=document.createElement('canvas');can.width=512;can.height=128;
   const ctx=can.getContext('2d');ctx.clearRect(0,0,512,128);
   ctx.fillStyle='#'+color.toString(16).padStart(6,'0');ctx.font='bold '+fontSize+'px system-ui';
   ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,256,64,498);
   const tx=new THREE.CanvasTexture(can);tx.colorSpace=THREE.SRGBColorSpace;
   return new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map:tx,transparent:true,side:THREE.DoubleSide,depthWrite:false}));
 };
 // Architecture and signage
 box(23,.25,20,tile,[0,-.17,0]);
 box(23,3.7,.26,cream,[0,1.75,-9.8]);box(.25,3.7,20,cream,[-11.4,1.75,0]);box(.25,3.7,20,cream,[11.4,1.75,0]);
 box(23,.24,.35,navy,[0,3.63,-9.62]);box(23,.1,.35,gold,[0,3.41,-9.55]);
 box(9,1,.06,navy,[0,2.77,-9.52]);
 const bankName=label('BANCO · DECISION LAB',8.2,.77,0xffffff,49);bankName.position.set(0,2.8,-9.46);scene.add(bankName);
 box(22.5,.016,1.9,mat(0xd8e5ed),[0,-.025,-.8]);
 for(let x=-10.5;x<=10.5;x+=1.5)box(.025,.003,19.5,mat(0xc6d8e1),[x,-.005,0]);
 for(let z=-9;z<=9;z+=1.5)box(22,.003,.025,mat(0xc6d8e1),[0,-.005,z]);
 // Glass entry facade, ticket kiosk and exit
 for(let x of [-10,-8.4,-6.8,6.8,8.4,10])box(.055,2.8,.07,steel,[x,1.5,9.65]);
 box(4,.09,.07,steel,[-7.6,2.95,9.65]);box(4,.09,.07,steel,[7.6,2.95,9.65]);
 const entryPlate=label('INGRESO',2.3,.47,0x0c648d,55);entryPlate.position.set(-7.4,2.45,9.45);scene.add(entryPlate);
 const exitPlate=label('SALIDA',2.1,.47,0x188167,55);exitPlate.position.set(7.5,2.45,9.45);scene.add(exitPlate);
 box(.9,1.4,.55,navy,[-8,.7,6.3]);box(.85,.16,.55,blue,[-8,1.47,6.3]);
 const ticket=label('TURNOS',.84,.24,0xffffff,55);ticket.position.set(-8,1.22,6.59);scene.add(ticket);
 // Waiting room seating
 for(let x of [-8.7,-7.5,-6.3]){
   box(.85,.12,.7,blue,[x,.47,1.8]);box(.85,.78,.11,navy,[x,.91,1.48]);
   cyl(.065,.065,.48,steel,[x-.32,.24,2.05]);cyl(.065,.065,.48,steel,[x+.32,.24,2.05]);
 }
 // Decorative plants
 for(const x of [-10,10]){cyl(.42,.34,.58,wood,[x,.29,-7.7]);cyl(.09,.11,1.15,mat(0x38644f),[x,1.1,-7.7]);for(let d=0;d<5;d++){let leaf=sphere(.38,mat(0x4d936e),[x+Math.sin(d*2.1)*.32,1.55+Math.cos(d*3)*.18,-7.7+Math.cos(d*2.1)*.24]);leaf.scale.set(.85,1.25,.75);}}
 // Queue rails on either side; avoid crossing central service aisle
 const rail=(x,z0,z1)=>{
   const length=Math.abs(z1-z0);for(let z=z0;z<=z1+.01;z+=2){cyl(.068,.075,1.0,steel,[x,.5,z]);sphere(.11,gold,[x,1.04,z]);}
   const bar=cyl(.035,.035,length,blue,[x,.88,(z0+z1)/2]);bar.rotation.x=Math.PI/2;
 };
 rail(-3.55,2.0,6.0);rail(3.55,2.0,6.0);
 const floorLabel=label('FILA DE ESPERA',4.1,.43,0x427c9a,40);floorLabel.rotation.x=-Math.PI/2;floorLabel.position.set(0,.022,7.0);scene.add(floorLabel);
 const counters=new Map(),people=new Map();let configured=-1;
 function buildCounter(i,count,clientId,draining){
   const row=i<8?0:Math.floor(i/8), col=i%8;
   const totalInRow=Math.min(8,Math.max(0,count-row*8));
   const x=(col-(totalInRow-1)/2)*2.55, z=-4.6-row*2.9;
   const group=new THREE.Group();scene.add(group);
   box(2.18,.94,.92,wood,[x,.47,z],group);
   box(2.2,.115,1.0,navy,[x,1.0,z],group);
   box(2.05,1.05,.055,glass,[x,1.76,z-.26],group);
   box(.055,1.1,.06,steel,[x-1.02,1.75,z-.25],group);box(.055,1.1,.06,steel,[x+1.02,1.75,z-.25],group);
   box(2.12,.07,.07,steel,[x,2.30,z-.25],group);
   const plaque=box(1.73,.43,.07,navy,[x,2.75,z-.15],group);
   const t=label('VENTANILLA '+(i+1),1.66,.28,0xffffff,54);t.position.set(x,2.75,z-.09);group.add(t);
   box(.62,.42,.10,mat(0x293b48),[x,1.45,z-.8],group);
   box(.54,.08,.31,steel,[x,1.12,z-.7],group);
   const dot=sphere(.12,mat(0x28ac75),[x+.88,2.52,z-.10],group);
   const staff=createHuman('staff-'+i,0x326d9b);staff.position.set(x,0,z-1.25);group.add(staff);
   counters.set(i,{group,x,z,spot:new THREE.Vector3(x,0,z+1.0),dot});
 }
 function createHuman(id,color){
   const g=new THREE.Group();const tone=[0xe6a978,0xc48b63,0xf0c3a4,0xa46f53][Math.abs(Number(id.toString().replace(/\D/g,''))||0)%4];
   const shirt=mat(color),skin=mat(tone),pants=mat(0x293c58),shoe=mat(0x242b35);
   cyl(.30,.37,.83,shirt,[0,1.03,0],g);
   sphere(.225,skin,[0,1.70,0],g);
   const hair=sphere(.233,mat(0x3a3030),[0,1.81,-.018],g);hair.scale.set(1,.42,1);
   for(const s of [-1,1]){
     const arm=cyl(.08,.1,.68,shirt,[s*.38,1.04,0],g);arm.rotation.z=s*.19;
     cyl(.115,.14,.68,pants,[s*.16,.36,0],g);
     box(.25,.12,.36,shoe,[s*.17,.07,.12],g);
   }
   const shadow=cyl(.31,.31,.012,mat(0x879ca5,{transparent:true,opacity:.25}),[0,.018,0],g);shadow.castShadow=false;
   return g;
 }
 function layoutStations(f){
   const current=Math.max(1,Number(f.active)||1),serverList=f.servers||[];
   const desired=new Set();
   for(let i=0;i<serverList.length;i++)if(i<current||serverList[i]!=null)desired.add(i);
   for(let i=0;i<current;i++)desired.add(i);
   for(const [i,c] of counters)if(!desired.has(i)){scene.remove(c.group);counters.delete(i);}
   if(current!==configured){configured=current;for(const c of counters.values()){scene.remove(c.group);}counters.clear();}
   for(const i of desired)if(!counters.has(i))buildCounter(i,current,serverList[i],i>=current);
   for(const [i,c] of counters)c.dot.material.color.setHex(i>=current?0xe59e53:(serverList[i]!=null?0xf1bd50:0x29b679));
 }
 function targets(f){
   const target=new Map(),q=(f.queue_ids||[]);
   // The people displayed are a literal subset of the backend queue; totals remain exact.
   q.slice(0,maxVisibleClients).forEach((id,j)=>{
     const column=j%5, row=Math.floor(j/5),x=(column-2)*1.05,z=2.1+row*.72;
     target.set(String(id),new THREE.Vector3(x,0,z));
   });
   (f.servers||[]).forEach((id,i)=>{
     if(id!=null && counters.has(i))target.set(String(id),counters.get(i).spot.clone());
   });
   return target;
 }
 function applyFrame(index){
   idx=Math.max(0,Math.min(frames.length-1,index));
   const f=frames[idx];
   layoutStations(f);
   const desired=targets(f);
   const now=performance.now();
   for(const [id,p] of desired){
     let obj=people.get(id);
     if(!obj){
       const shades=[0x387bb0,0xb35f68,0x568f71,0xb78a47,0x946ea0];
       const person=createHuman(id,shades[(Number(id)||0)%shades.length]);
       person.position.set(-7.5,0,8.8);scene.add(person);
       obj={person,target:p.clone(),leaving:false,leaveAt:0};
       people.set(id,obj);
     }
     obj.target.copy(p);obj.leaving=false;obj.leaveAt=0;
   }
   for(const [id,obj] of people){
     if(!desired.has(id)&&!obj.leaving){
       obj.leaving=true;obj.leaveAt=now+1700;obj.target.set(7.7,0,9.2);
     }
   }
   $('stat-time').textContent=Number(f.t||0).toFixed(1)+' min';
   $('stat-active').textContent=Number(f.active||0);
   $('stat-queue').textContent=Number(f.queue||0);
   $('stat-served').textContent=Number(f.completed||0);
   $('stat-lost').textContent=Number(f.blocked||0)+Number(f.abandoned||0);
   $('event-count').textContent='Evento '+idx+' / '+(frames.length-1);
   const titles={start:'Inicio de jornada',arrival:'Llegada de cliente',departure:'Atención terminada',decision:'Cambio de dotación',shift:'Cambio de turno',incident:'Incidente',end:'Fin de jornada',abandon:'Abandono'};
   $('event-kind').textContent=titles[f.kind]||String(f.kind||'Evento');
   $('seek').value=idx;
   $('back').disabled=preview||idx===0;
   $('next').disabled=preview||idx===frames.length-1;
   $('visual-limit').textContent=Number(f.queue||0)>maxVisibleClients?'Se muestran hasta '+maxVisibleClients+' clientes en espera; el contador refleja el total real.':'';
   if(idx===frames.length-1&&!preview){playing=false;$('state').textContent='JORNADA FINALIZADA';$('state').className='state finished';$('play').textContent='▶ Repetir';}
 }
 function setPlaying(p){
   if(preview)return;
   if(p && idx>=frames.length-1)applyFrame(0);
   playing=p;accumulator=0;
   $('play').textContent=playing?'⏸ Pausar':'▶ '+(idx===0?'Iniciar':'Continuar');
   $('state').textContent=playing?'SIMULACIÓN EN CURSO':'SIMULACIÓN EN PAUSA';
   $('state').className='state '+(playing?'running':'ready');
 }
 $('play').addEventListener('click',()=>setPlaying(!playing));
 $('reset').addEventListener('click',()=>{setPlaying(false);applyFrame(0);});
 $('back').addEventListener('click',()=>{setPlaying(false);applyFrame(idx-1);});
 $('next').addEventListener('click',()=>{setPlaying(false);applyFrame(idx+1);});
 $('speed').addEventListener('change',()=>{speed=Number($('speed').value)||1;});
 $('seek').addEventListener('input',()=>{setPlaying(false);applyFrame(Number($('seek').value));});
 function resize(){const rect=stage.getBoundingClientRect();if(rect.width<1||rect.height<1)return;camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();renderer.setSize(rect.width,rect.height,false);}
 new ResizeObserver(resize).observe(stage);resize();
 applyFrame(0);
 $('loading').remove();
 function animate(ms){
   requestAnimationFrame(animate);
   const dt=Math.min(.06,(ms-(last||ms))/1000);last=ms;
   if(playing){accumulator+=dt*speed;while(accumulator>=.72 && playing){applyFrame(idx+1);accumulator-=.72;}}
   for(const [id,o] of people){
     const rate=Math.min(1,dt*3.7),old=o.person.position;
     old.lerp(o.target,rate);
     const moving=old.distanceTo(o.target)>.07;
     o.person.children[0].rotation.z=moving?Math.sin(ms*.011+Number(id))*.065:0;
     if(o.leaving && ms>o.leaveAt){scene.remove(o.person);people.delete(id);}
   }
   controls.update();renderer.render(scene,camera);
 }
 requestAnimationFrame(animate);
}catch(err){$('loading').textContent='Error al cargar el escenario 3D: '+(err&&err.message||err);}
</script>
</body>
</html>"""
