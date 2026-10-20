(() => {
"use strict";
const e=id=>document.getElementById(id);let count=2;
const defaults=[["Recepción",5,2],["Atención",8,3],["Pago",4,2],["Entrega",6,2]];
function render(){const host=e("network-stages");host.innerHTML=Array.from({length:count},(_,i)=>{const d=defaults[i];return '<div class="network-stage"><b>Etapa '+(i+1)+'</b><label>Nombre<input class="net-name" value="'+d[0]+'"></label><label>Servicio (min)<input class="net-service" type="number" min=".1" step=".1" value="'+d[1]+'"></label><label>Servidores<input class="net-servers" type="number" min="1" max="20" value="'+d[2]+'"></label></div>'}).join("")}
function payload(){return {arrival_min:Number(e("net-arrival").value),horizon:Number(e("net-horizon").value),seed:2026,stages:[...document.querySelectorAll(".network-stage")].map(row=>({name:row.querySelector(".net-name").value,service_min:Number(row.querySelector(".net-service").value),servers:Number(row.querySelector(".net-servers").value)}))}}
async function run(ev){ev.preventDefault();e("network-status").textContent="Simulando red…";const token=document.cookie.split("; ").find(v=>v.startsWith("csrftoken="))?.split("=")[1]||"";
try{const r=await fetch("/api/network/",{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":token},body:JSON.stringify(payload())});const d=await r.json();if(!r.ok||!d.ok)throw Error(d.error||"Error");
e("network-kpis").innerHTML=[["Llegadas",d.arrivals],["Completados",d.completed],["Throughput",d.throughput_rate.toFixed(2)+"/h"],["Tiempo sistema",d.avg_system.toFixed(2)+" min"]].map(x=>'<article><small>'+x[0]+'</small><b>'+x[1]+'</b></article>').join("");
let bottleneck=d.stages.reduce((a,b)=>a.utilization>b.utilization?a:b);e("network-status").textContent="Cuello de botella probable: "+bottleneck.name+" · utilización "+(bottleneck.utilization*100).toFixed(1)+"%.";
e("network-stage-results").innerHTML=d.stages.map((x,i)=>'<article><span>Etapa '+(i+1)+'</span><b>'+x.name+'</b><small>Wq '+x.avg_wait.toFixed(2)+' min · Lq '+x.avg_queue.toFixed(2)+' · ρ '+(x.utilization*100).toFixed(1)+'% · cola máx. '+x.max_queue+'</small></article>').join("");
if(window.Plotly)Plotly.react("network-chart",d.stages.map((x,i)=>({x:d.frames.map(f=>f.t),y:d.frames.map(f=>f.queues[i]),mode:"lines",type:"scatter",line:{shape:"hv"},name:x.name})),{margin:{t:20,l:45,r:15,b:45},xaxis:{title:"Tiempo (min)"},yaxis:{title:"Clientes en cola"},legend:{orientation:"h"}},{responsive:true,displayModeBar:false});
}catch(err){e("network-status").textContent=err.message}}
e("net-add").onclick=()=>{if(count<4){count++;render()}};e("net-remove").onclick=()=>{if(count>2){count--;render()}};e("network-form").addEventListener("submit",run);render();
})();