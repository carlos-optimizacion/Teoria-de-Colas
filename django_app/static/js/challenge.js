(() => {
const el=id=>document.getElementById(id),scenarios=SCENARIOS;
let last=null,timer=null,step=0;
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function setup(){let c=scenarios[el('challenge-scenario').value];el('challenge-brief').innerHTML='<p><b>Presupuesto:</b> S/ '+c.budget+'</p><p><b>Meta SLA:</b> '+(c.sla_target*100)+'% antes de '+c.sla_min+' minutos</p><p><b>Interarribo:</b> '+c.arrival_min+' min · <b>Servicio:</b> '+c.service_min+' min</p><p><b>Incidente:</b> '+esc(c.incident)+'</p>';
el('challenge-staff').innerHTML=Array.from({length:8},(_,i)=>'<label class="hourrow">Hora '+(i+1)+' <input class="challenge-server" type="number" min="1" max="'+c.max_servers+'" step="1" value="'+Math.min(c.max_servers,4)+'"></label>').join('');
}
function kpis(m,score){return [['Puntos',score+'/100'],['SLA',(100*m.sla).toFixed(1)+'%'],['Costo total','S/ '+m.total_cost.toFixed(2)],['Bloqueos',m.blocked.toFixed(1)],['Espera',m.avg_wait.toFixed(1)+' min'],['En cola',m.avg_queue.toFixed(2)],['Utilización',(m.utilization*100).toFixed(1)+'%'],['Pendientes al cierre',m.unserved_at_close.toFixed(1)]].map(([a,b])=>'<div class="mission-kpi"><small>'+a+'</small><b>'+b+'</b></div>').join('')}
async function run(){clearInterval(timer);el('challenge-status').textContent='Calculando réplicas…';
try {const payload={scenario:el('challenge-scenario').value,staffing:[...document.querySelectorAll('.challenge-server')].map(e=>Number(e.value)),replications:Number(el('challenge-reps').value),seed:2026};
const token=document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))?.split('=')[1]||'';
const r=await fetch('/api/challenge/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':token},body:JSON.stringify(payload)});const d=await r.json();if(!r.ok||!d.ok)throw Error(d.error||'Error de evaluación');
last={...d,payload};const m=d.metrics;el('challenge-status').className='challenge-status '+(!d.passes.budget||!d.passes.sla?'challenge-warning':'');
el('challenge-status').textContent=(d.passes.budget&&d.passes.sla?'Objetivos cumplidos. ':'Una o más metas incumplidas. ')+'Puntuación: '+d.score+' / 100.';
el('challenge-kpis').innerHTML=kpis(m,d.score);
const ci=d.confidence_95||{};const interval=(key,unit='')=>ci[key]&&ci[key].low!=null?ci[key].low.toFixed(2)+' a '+ci[key].high.toFixed(2)+unit:'No disponible (requiere más réplicas)';
el('challenge-analysis').innerHTML='<p><b>IC 95% exploratorio del costo total:</b> S/ '+interval('total_cost')+'</p><p><b>IC 95% exploratorio de espera:</b> '+interval('avg_wait',' min')+'</p><p><b>Personal:</b> S/ '+m.staff_cost.toFixed(2)+' · <b>Espera:</b> S/ '+m.waiting_cost.toFixed(2)+' · <b>Clientes bloqueados:</b> S/ '+m.lost_cost.toFixed(2)+'</p><p><b>Meta de presupuesto:</b> '+(d.passes.budget?'Cumplida':'No cumplida')+' · <b>Meta de servicio:</b> '+(d.passes.sla?'Cumplida':'No cumplida')+'</p><p>'+esc(d.method)+'</p>';
el('challenge-play').disabled=false;el('challenge-export').disabled=false;step=0;showFrame();
if(window.Plotly)Plotly.react('challenge-plot',[{x:d.series.map(x=>x.t),y:d.series.map(x=>x.queue),type:'scatter',mode:'lines',line:{shape:'hv'},name:'Clientes en cola'}],{margin:{t:15,b:40,l:45,r:10},xaxis:{title:'Minutos'},yaxis:{title:'Cola'}},{displayModeBar:false});
}catch(e){el('challenge-status').textContent=e.message;}
}
function showFrame(){if(!last)return;let f=last.events[Math.min(step,last.events.length-1)]||{t:0,queue:0,busy:0};
el('c-clock').textContent=f.t.toFixed(1)+' min';el('c-queue').textContent=f.queue;el('c-busy').textContent=f.busy;el('c-arrivals').textContent=last.events.slice(0,step+1).filter(e=>e.kind==='arrival').length;
el('challenge-event').textContent='Evento '+(step+1)+'/'+last.events.length+' · Cliente '+(f.client||'—')+' · '+(f.kind==='arrival'?'llegada':'salida')+' · '+f.active+' servidores habilitados';
}
function play(){if(!last)return;if(timer){clearInterval(timer);timer=null;el('challenge-play').textContent='▶ Continuar';return;}if(step>=last.events.length-1)step=0;el('challenge-play').textContent='⏸ Pausar';
timer=setInterval(()=>{step=Math.min(step+Number(el('challenge-speed').value),last.events.length-1);showFrame();if(step>=last.events.length-1){clearInterval(timer);timer=null;el('challenge-play').textContent='↻ Repetir';}},180);}
el('challenge-scenario').addEventListener('change',setup);el('challenge-run').addEventListener('click',run);el('challenge-play').addEventListener('click',play);el('challenge-export').addEventListener('click',()=>{if(!last)return;const b=new Blob([JSON.stringify(last,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='decision-lab-'+last.scenario+'.json';a.click();URL.revokeObjectURL(a.href);});setup();
})();
