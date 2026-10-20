(() => {
"use strict";
const el=id=>document.getElementById(id);
const scenarios=JSON.parse(el("challenge-config").textContent);
const scene = window.DecisionLabScene.mount(document.querySelector(".scene-art-wrap"));
let last=null,baseline=null,actions=[],step=0,timer=null,updating=false;
const money=v=>"S/ "+Number(v).toFixed(2);
const decimal=(v,n=2)=>Number(v).toFixed(n);
const percentage=v=>(100*Number(v)).toFixed(1)+"%";
const person=id=>'<span class="arena-person" title="Cliente '+Number(id)+'">'+Number(id)+'</span>';

function stop(){
  if(timer!==null)clearInterval(timer);
  timer=null;
  el("challenge-play").textContent="▶ Reproducir";
}
function setup(){
  stop();last=null;baseline=null;actions=[];step=0;
  const scenarioKey=el("challenge-scenario").value;
  const c=scenarios[scenarioKey];
  const artBase=el("scene-shell").dataset.assetsBase;
  el("c-scene-art").src=artBase+scenarioKey+".svg";
  el("scenario-preview-image").src=artBase+scenarioKey+".svg";
  el("scene-status-text").textContent="Escenario "+c.sector+" · listo";
  el("scene-shell").dataset.sector=scenarioKey;
  document.querySelectorAll(".sector-card").forEach(card=>{card.classList.toggle("is-selected",card.dataset.sector===scenarioKey);card.setAttribute("aria-pressed",String(card.dataset.sector===scenarioKey));});
  scene.render({servers:Array(c.max_servers).fill(null),active:Math.min(c.max_servers,4),queue_ids:[],queue_length:0});
  el("scene-arrivals").textContent="0";
  const title=document.getElementById("target-scene-title");if(title)title.textContent="Simulación: "+c.name+" ("+c.model+")";
  el("challenge-arrival").value=c.arrival_min;
  el("challenge-service").value=c.service_min;
  el("challenge-capacity").value=c.capacity;
  el("challenge-staff-cost").value=c.staff_hour;
  el("challenge-wait-cost").value=c.wait_hour;
  el("challenge-sla-min").value=c.sla_min;
  el("challenge-sla-target").value=c.sla_target;
  el("challenge-uniform-servers").max=c.max_servers;
  el("challenge-uniform-servers").value=Math.min(c.max_servers,4);
  el("challenge-brief").innerHTML='<div><b>Modelo:</b> '+c.model+'</div><div><b>Presupuesto:</b> '+money(c.budget)+'</div><div><b>Objetivo:</b> '+percentage(c.sla_target)+' de admitidos con espera ≤ '+c.sla_min+' minutos</div><div><b>Llegadas:</b> cada '+c.arrival_min+' min</div><div><b>Servicio:</b> '+c.service_min+' min</div><div><b>Evento:</b> '+c.incident+'</div>';
  el("challenge-staff").innerHTML=Array.from({length:8},(_,i)=>'<label class="hourrow" for="hour-'+i+'">Hora '+(i+1)+' <input id="hour-'+i+'" class="challenge-server" type="number" min="1" max="'+c.max_servers+'" step="1" value="'+Math.min(c.max_servers,4)+'"></label>').join("");
  el("challenge-intervene-count").max=c.max_servers;
  el("challenge-intervene-count").value=Math.min(c.max_servers,4);
  el("challenge-status").textContent="Configura el escenario y pulsa «Evaluar y simular jornada».";
  el("challenge-kpis").replaceChildren();el("challenge-achievements").replaceChildren();
  el("challenge-analysis").textContent="Los resultados y sus intervalos de incertidumbre aparecerán al evaluar.";
  el("challenge-comparison").replaceChildren();
  el("challenge-actions").replaceChildren();
  el("challenge-badge").textContent="Sin evaluar";
  for(const name of ["challenge-play","challenge-restart","challenge-scrub","challenge-intervene","challenge-export"])el(name).disabled=true;
  el("c-clock").textContent="00:00";el("c-queue").textContent="0";el("c-busy").textContent="0";
  el("c-completed").textContent="0";el("c-arrivals").textContent="0 clientes recibidos";
  el("c-queue-people").textContent="Sin clientes";el("c-server-list").replaceChildren();
  el("c-progress-label").textContent="Evento 0/0";el("c-arrival-label").textContent="0 llegadas";
  el("c-blocked").textContent="0 bloqueados";
  for(const [id,value] of Object.entries({"live-arrivals":"0","live-completed":"0","live-waiting":"0","live-capacity":"0 / 0","live-rejected":"0"}))el(id).textContent=value;
  if(window.Plotly)Plotly.purge(el("challenge-plot"));
}
function payload(){
  return {
    scenario:el("challenge-scenario").value,
    staffing:[...document.querySelectorAll(".challenge-server")].map(e=>Number(e.value)),
    replications:Number(el("challenge-reps").value),
    arrival_min:Number(el("challenge-arrival").value),
    service_min:Number(el("challenge-service").value),
    capacity:Number(el("challenge-capacity").value),
    staff_hour:Number(el("challenge-staff-cost").value),
    wait_hour:Number(el("challenge-wait-cost").value),
    sla_min:Number(el("challenge-sla-min").value),
    sla_target:Number(el("challenge-sla-target").value),
    patience_min:Number(el("challenge-patience").value),
    priority_share:Number(el("challenge-priority").value),
    seed:2026,
    actions:actions.map(x=>({...x}))
  };
}
const kpis=[["Puntuación","score"],["SLA","sla"],["Costo total","total_cost"],["Espera al iniciar","avg_wait"],
  ["Cola media","avg_queue"],["Utilización","utilization"],["Bloqueados","blocked"],["Abandonos","abandoned"],["Pendientes al cierre","unserved_at_close"]];
function showKpis(d){
  const m=d.metrics;
  el("challenge-kpis").innerHTML=kpis.map(([label,key])=>{
    const value=key==="score"?d.score+" / 100":key==="sla"||key==="utilization"?percentage(m[key]):key==="total_cost"?money(m[key]):key==="avg_wait"?decimal(m[key])+" min":decimal(m[key],key==="blocked"||key==="abandoned"||key==="unserved_at_close"?1:2);
    const node=document.createElement("div");
    node.className="arena-kpi";
    node.innerHTML="<small>"+label+"</small><b>"+value+"</b>";
    return node.outerHTML;
  }).join("");
  el("challenge-achievements").innerHTML=(d.achievements||[]).map(x=>"<span>★ "+x+"</span>").join("");
  const medal=d.passes.sla&&d.passes.budget?(d.score>=90?"Oro":d.score>=80?"Plata":d.score>=70?"Bronce":"Misión cumplida"):"En entrenamiento";
  el("challenge-badge").textContent=medal;
  // Personal progress is stored only in this browser, not sent to a leaderboard.
  try {const key="decisionlab.best."+d.scenario;const best=Number(localStorage.getItem(key)||0);if(d.score>best)localStorage.setItem(key,String(d.score));}catch(e){}
  el("challenge-status").className="arena-status "+(d.passes.sla&&d.passes.budget?"arena-success":"arena-warning");
  el("challenge-status").textContent=(d.passes.sla&&d.passes.budget?"Ambas metas satisfechas. ":"Revisa los límites de presupuesto y servicio. ")+"Resultado: "+d.score+" / 100 puntos.";
}
function showAnalysis(d){
  const m=d.metrics,ci=d.confidence_95||{};
  const interval=(key,suffix="")=>ci[key]&&ci[key].low!=null?decimal(ci[key].low)+" – "+decimal(ci[key].high)+suffix:"No disponible con una réplica";
  el("challenge-analysis").innerHTML="<p><b>Personal:</b> "+money(m.staff_cost)+" · <b>Costo de espera:</b> "+money(m.waiting_cost)+" · <b>Pérdida por bloqueo:</b> "+money(m.lost_cost)+"</p>"
  +"<p><b>Intervalo exploratorio 95% del costo:</b> "+interval("total_cost"," soles")+" · <b>Espera:</b> "+interval("avg_wait"," min")+"</p>"
  +"<p><b>Presupuesto:</b> "+(d.passes.budget?"Cumplido":"No cumplido")+" · <b>Objetivo de servicio:</b> "+(d.passes.sla?"Cumplido":"No cumplido")+"</p><p>"+d.method+"</p>";
  if(!baseline)baseline=d;
  const b=baseline.metrics;
  if(baseline!==d){
    const rows=[["SLA",percentage(b.sla),percentage(m.sla)],["Costo total",money(b.total_cost),money(m.total_cost)],
      ["Espera",decimal(b.avg_wait)+" min",decimal(m.avg_wait)+" min"],["Puntuación",baseline.score,d.score]];
    el("challenge-comparison").innerHTML="<b>Comparación con tu primera estrategia (misma semilla)</b><table><thead><tr><th>Indicador</th><th>Inicial</th><th>Actual</th></tr></thead><tbody>"+rows.map(r=>"<tr>"+r.map(x=>"<td>"+x+"</td>").join("")+"</tr>").join("")+"</tbody></table>";
  }
  el("challenge-actions").textContent=actions.length?"Intervenciones: "+actions.map(x=>"min "+x.minute+" → "+x.servers+" servidores").join(" · "):"Aún no se han tomado decisiones durante la jornada.";
}
function clock(t){const whole=Math.max(0,Math.floor(t));return String(Math.floor(whole/60)).padStart(2,"0")+":"+String(whole%60).padStart(2,"0");}
function renderSceneActors(frame) {
  scene.render(frame);
  el("scene-arrivals").textContent = String(frame.arrivals || 0);
  el("scene-status-text").textContent =
    frame.kind === "blocked" ? "Capacidad completa · cliente rechazado" :
    frame.kind === "incident" ? "Incidente: capacidad reducida" :
    frame.kind === "decision" ? "Nueva dotación aplicada" :
    frame.kind === "end" ? "Jornada finalizada" :
    frame.kind === "start" ? "Sistema listo" :
    "Operación en curso · " + frame.active + " puestos habilitados";
  el("scene-shell").dataset.event = frame.kind;
}
function renderFrame(){
  if(!last||!last.events.length)return;
  const f=last.events[Math.min(step,last.events.length-1)];
  el("c-clock").textContent=clock(f.t);
  el("c-queue").textContent=f.queue;el("c-busy").textContent=f.busy;
  el("c-completed").textContent=f.completed;el("c-arrivals").textContent=f.arrivals+" clientes recibidos";
  el("c-blocked").textContent=f.blocked+" bloqueados";
  el("live-arrivals").textContent=String(f.arrivals);
  el("live-completed").textContent=String(f.completed);
  el("live-waiting").textContent=String(f.queue);
  el("live-capacity").textContent=f.busy+" / "+f.active;
  el("live-rejected").textContent=String(f.blocked);
  el("c-progress-label").textContent="Evento "+step+"/"+(last.events.length-1);
  el("c-arrival-label").textContent=f.arrivals+" llegadas";
  el("challenge-scrub").value=step;
  const ids=f.queue_ids||[];
  el("c-queue-people").innerHTML=ids.length?ids.map(person).join("")+(f.queue>ids.length?'<span>+'+(f.queue-ids.length)+'</span>':""):"<i>Sin clientes esperando</i>";
  el("c-server-list").innerHTML=(f.servers||[])
    .map((cid,i)=>({cid,i})).filter(({cid,i})=>i<f.active || cid!=null)
    .map(({cid,i})=>{
      const active=i<f.active,occupied=cid!=null;
      return '<div class="arena-server '+(!active?'is-off':occupied?'is-busy':"")+'"><strong>P'+(i+1)+'</strong>'+(occupied?person(cid):'<span>'+(active?'Libre':'Cierre pendiente')+'</span>')+'</div>';
    }).join("");
  const messages={start:"Comienza la jornada.",arrival:"El cliente "+f.client+" ingresa al sistema.",blocked:"Cliente "+f.client+" rechazado por capacidad completa.",departure:"Finaliza la atención del cliente "+f.client+".",shift:"Cambio programado de dotación.",decision:"Decisión gerencial aplicada: "+f.active+" servidores disponibles.",incident:"Evento de indisponibilidad de un servidor.",abandon:"El cliente "+f.client+" abandona la cola por superar su paciencia.",end:"Fin de la jornada."};
  el("challenge-event").textContent=messages[f.kind]||"Evento operativo.";
  renderSceneActors(f);
}
function seekTime(t){
  const frames=last.events;
  let lo=0,hi=frames.length-1;
  while(lo<hi){const mid=Math.ceil((lo+hi)/2);if(frames[mid].t<=t)lo=mid;else hi=mid-1;}
  step=lo;renderFrame();
}
function showChart(d){
  if(!window.Plotly)return;
  const series=d.series||[];
  window.Plotly.react(el("challenge-plot"),[
    {x:series.map(v=>v.t),y:series.map(v=>v.queue),mode:"lines",type:"scatter",line:{shape:"hv",width:2,color:"#107eab"},name:"En cola"},
    {x:series.map(v=>v.t),y:series.map(v=>v.busy),mode:"lines",type:"scatter",line:{shape:"hv",width:2,color:"#2a9975"},name:"En servicio"}
  ],{margin:{t:25,l:42,r:12,b:45},paper_bgcolor:"#fff",plot_bgcolor:"#fff",
    legend:{orientation:"h",y:1.15},xaxis:{title:"Tiempo simulado (min)",gridcolor:"#e5eef3"},
    yaxis:{title:"Clientes",rangemode:"tozero",gridcolor:"#e5eef3"}},{responsive:true,displayModeBar:false});
}
async function run({keepTime=false}={}){
  if(updating)return;
  updating=true;stop();
  const cursor=keepTime&&last?last.events[step].t:0;
  const button=el("challenge-run");
  button.disabled=true;
  el("challenge-status").textContent="Ejecutando réplicas y calculando indicadores…";
  try{
    // Interventions freeze the initial staffing and statistical settings.
    // They cannot silently rewrite already simulated decisions.
    const req=keepTime&&last?{...last.payload,actions:actions.map(x=>({...x}))}:payload();
    const token=document.cookie.split("; ").find(v=>v.startsWith("csrftoken="))?.split("=")[1]||"";
    const r=await fetch("/api/challenge/",{method:"POST",credentials:"same-origin",
      headers:{"Content-Type":"application/json","X-CSRFToken":token},body:JSON.stringify(req)});
    const d=await r.json();
    if(!r.ok||!d.ok)throw new Error(d.error||"No se pudo ejecutar el desafío.");
    last={...d,payload:req};
    const reportLink=document.getElementById("challenge-report-link");
    if(reportLink && d.run_id){reportLink.href="/reportes/"+d.run_id+"/";reportLink.hidden=false;}
    if(d.progress){const level=document.getElementById("top-user-level"),xp=document.getElementById("top-user-xp"),coins=document.getElementById("top-user-coins");if(level)level.textContent=d.progress.level;if(xp)xp.textContent=d.progress.xp;if(coins)coins.textContent=d.progress.coins;}
    const saveButton=document.getElementById("challenge-save-scenario");if(saveButton)saveButton.disabled=false;
    showKpis(d);showAnalysis(d);showChart(d);
    for(const id of ["challenge-play","challenge-restart","challenge-scrub","challenge-intervene","challenge-export"])el(id).disabled=false;
    el("challenge-scrub").max=Math.max(0,last.events.length-1);
    step=0;
    if(keepTime)seekTime(cursor);else renderFrame();
  }catch(e){
    el("challenge-status").className="arena-status arena-warning";
    el("challenge-status").textContent=e.message;
  }finally{updating=false;button.disabled=false;}
}
function play(){
  if(!last)return;
  if(timer!==null){stop();return;}
  if(step>=last.events.length-1)step=0;
  el("challenge-play").textContent="⏸ Pausar";
  timer=setInterval(()=>{
    step=Math.min(last.events.length-1,step+Number(el("challenge-speed").value));
    renderFrame();
    if(step>=last.events.length-1)stop();
  },220);
}
function intervention(){
  if(!last)return;
  const duration=last.config.duration;
  const cursor=last.events[step].t;
  const minute=Math.max(1,Math.floor(cursor)+1,actions.length?actions[actions.length-1].minute+1:1);
  if(minute>=duration){el("challenge-status").textContent="No pueden modificarse recursos al cierre de la jornada.";return;}
  const servers=Number(el("challenge-intervene-count").value);
  if(!Number.isInteger(servers)||servers<1||servers>last.config.max_servers){
    el("challenge-status").textContent="Indica un número válido de servidores.";return;
  }
  actions.push({minute,servers});
  run({keepTime:true});
}
function exportGame(){
  if(!last)return;
  const blob=new Blob([JSON.stringify(last,null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a");a.href=url;a.download="decision-lab-"+last.scenario+"-partida.json";a.click();
  setTimeout(()=>URL.revokeObjectURL(url),2000);
}
const uniformServers=document.getElementById("challenge-uniform-servers");
uniformServers.addEventListener("change",()=>{
  const count=Number(uniformServers.value);
  document.querySelectorAll(".challenge-server").forEach(input=>input.value=String(count));
});
el("challenge-scenario").addEventListener("change",setup);
document.querySelectorAll(".sector-card").forEach(card=>card.addEventListener("click",()=>{
  el("challenge-scenario").value=card.dataset.sector;
  setup();
  el("mission-panel").scrollIntoView({behavior:window.matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"});
}));
el("challenge-run").addEventListener("click",()=>{baseline=null;run();});
el("challenge-play").addEventListener("click",play);
el("challenge-restart").addEventListener("click",()=>{stop();step=0;renderFrame();});
el("challenge-scrub").addEventListener("input",e=>{stop();step=Number(e.target.value);renderFrame();});
el("challenge-intervene").addEventListener("click",intervention);
el("challenge-export").addEventListener("click",exportGame);

async function saveScenario(){
  if(!last)return;
  const name=window.prompt("Nombre del escenario",""+last.title+" · estrategia");
  if(!name)return;
  const token=document.cookie.split("; ").find(v=>v.startsWith("csrftoken="))?.split("=")[1]||"";
  const response=await fetch("/api/scenario/save/",{method:"POST",credentials:"same-origin",
    headers:{"Content-Type":"application/json","X-CSRFToken":token},
    body:JSON.stringify({name,scenario:last.scenario,payload:last.payload})});
  const data=await response.json();
  if(!response.ok||!data.ok){el("challenge-status").textContent=data.error||"No se pudo guardar.";return;}
  el("challenge-status").textContent="Escenario guardado como «"+data.name+"».";
}
const saveButton=document.getElementById("challenge-save-scenario");
if(saveButton)saveButton.addEventListener("click",saveScenario);


function restoreSavedScenario(){
  const script=document.getElementById("initial-saved-scenario");
  if(!script)return;
  try{
    const saved=JSON.parse(script.textContent);
    if(saved.scenario && scenarios[saved.scenario]){
      el("challenge-scenario").value=saved.scenario;
      setup();
    }
    const values={
      "challenge-reps":saved.replications,
      "challenge-arrival":saved.arrival_min,
      "challenge-service":saved.service_min,
      "challenge-capacity":saved.capacity,
      "challenge-staff-cost":saved.staff_hour,
      "challenge-wait-cost":saved.wait_hour,
      "challenge-sla-min":saved.sla_min,
      "challenge-sla-target":saved.sla_target,
      "challenge-patience":saved.patience_min,
      "challenge-priority":saved.priority_share
    };
    Object.entries(values).forEach(([id,value])=>{if(value!==undefined&&value!==null)el(id).value=String(value);});
    if(Array.isArray(saved.staffing)){
      document.querySelectorAll(".challenge-server").forEach((input,index)=>{if(saved.staffing[index]!=null)input.value=String(saved.staffing[index]);});
      if(saved.staffing.length && saved.staffing.every(v=>v===saved.staffing[0]))el("challenge-uniform-servers").value=String(saved.staffing[0]);
    }
    actions=Array.isArray(saved.actions)?saved.actions.map(x=>({...x})):[];
    el("challenge-actions").textContent=actions.length?"Intervenciones restauradas: "+actions.map(x=>"min "+x.minute+" → "+x.servers).join(" · "):"Escenario restaurado sin intervenciones.";
    el("challenge-status").textContent="Estrategia guardada restaurada. Pulsa «Evaluar y simular».";
  }catch(error){console.error("No se pudo restaurar el escenario guardado",error);}
}

setup();
restoreSavedScenario();
})();
