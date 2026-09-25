const form = document.getElementById('lab-form');
const $ = id => document.getElementById(id);
const pct = x => x == null ? '—' : `${(x * 100).toFixed(1)}%`;
const num = (x, digits=2) => x == null ? '—' : Number(x).toFixed(digits);
const min = x => x == null ? '∞' : `${Number(x).toFixed(2)} min`;

function csrfToken(){ return document.cookie.split('; ').find(r=>r.startsWith('csrftoken='))?.split('=')[1] || ''; }
function bindRange(id, out){ const el=$(id); if(!el) return; const o=$(out); const sync=()=>o.textContent=el.value; el.addEventListener('input', sync); sync(); }
[['t-llegada','arrival-out'],['t-atencion','service-out'],['servers','servers-out'],['horizon','horizon-out'],['replications','replications-out']].forEach(x=>bindRange(...x));

async function runLab(event){
  if(event) event.preventDefault();
  const payload={model:form.dataset.model,t_llegada:+$('t-llegada').value,t_atencion:+$('t-atencion').value,servers:+$('servers').value,horizon:+$('horizon').value,replications:+$('replications').value};
  $('alert').innerHTML='<div class="notice">Calculando modelo analítico y simulación…</div>';
  try{
    const res=await fetch('/api/queue/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrfToken()},body:JSON.stringify(payload)});
    const data=await res.json(); if(!data.ok) throw new Error(data.error||'Error de cálculo'); render(data);
  }catch(err){ $('alert').innerHTML=`<div class="notice danger">${err.message}</div>`; }
}

function render(data){
  const a=data.analytic, s=data.simulation;
  $('rho').textContent=pct(a.rho); $('wq').textContent=min(a.wq_min); $('lq').textContent=num(a.lq); $('pwait').textContent=pct(a.p_wait);
  $('alert').innerHTML=a.stable?'<div class="notice success">Sistema estable bajo los supuestos del modelo.</div>':'<div class="notice danger">Sistema inestable: la demanda iguala o supera la capacidad agregada.</div>';

  Plotly.react('comparison-chart',[{x:['Wq analítico','Wq simulado'],y:[a.wq_min||0,s.wq_min],type:'bar',text:[a.wq_min==null?'∞':a.wq_min.toFixed(2),s.wq_min.toFixed(2)],textposition:'auto'}],{title:'Espera promedio (min)',margin:{t:45,l:45,r:15,b:40},paper_bgcolor:'transparent',plot_bgcolor:'transparent',showlegend:false},{responsive:true});
  Plotly.react('utilization-chart',[{x:['Analítico','Simulado'],y:[a.rho*100,s.utilization*100],type:'bar',text:[`${(a.rho*100).toFixed(1)}%`,`${(s.utilization*100).toFixed(1)}%`],textposition:'auto'}],{title:'Utilización (%)',margin:{t:45,l:45,r:15,b:40},paper_bgcolor:'transparent',plot_bgcolor:'transparent',showlegend:false},{responsive:true});
  Plotly.react('queue-chart',[{x:s.queue_series.map(p=>p.t),y:s.queue_series.map(p=>p.q),mode:'lines',line:{shape:'hv',width:3},fill:'tozeroy'}],{title:`Evolución de cola · réplica representativa (${s.horizon_min} min)`,xaxis:{title:'Tiempo (min)'},yaxis:{title:'Clientes esperando',rangemode:'tozero'},margin:{t:50,l:55,r:20,b:55},paper_bgcolor:'transparent',plot_bgcolor:'transparent'},{responsive:true});

  const i=data.interpretation; const cards=[['🔎','¿Qué está pasando?',i.que_pasa],['🧩','¿Por qué ocurre?',i.por_que],['🏭','¿Qué significa operativamente?',i.operacion],['🔧','¿Qué podrías cambiar?',i.accion],['🎓','¿Qué debes aprender?',i.aprendizaje]];
  $('interpretation').innerHTML=cards.map(c=>`<article><span>${c[0]}</span><div><b>${c[1]}</b><p>${c[2]}</p></div></article>`).join('');
}
form.addEventListener('submit',runLab); window.addEventListener('DOMContentLoaded',()=>runLab());
