(() => {
"use strict";
const get=id=>document.getElementById(id),num=id=>Number(get(id).value);
const percent=v=>v==null?"—":(v*100).toFixed(1)+"%";
const format=v=>v==null?"—":Number(v).toFixed(2);
function csrf(){return document.cookie.split("; ").find(x=>x.startsWith("csrftoken="))?.split("=")[1]||"";}
async function run(){
  const button=get("lab-run");
  button.disabled=true;
  get("lab-result").textContent="Evaluando el modelo seleccionado...";
  try{
    const payload={
      model:get("lab-model").value,
      t_llegada:num("lab-arrival"),t_atencion:num("lab-service"),
      servers:num("lab-servers"),capacity:num("lab-capacity"),
      cv:num("lab-cv"),waiting_places:num("lab-waiting"),
      n:num("lab-n"),horizon:240,replications:15
    };
    if(!Number.isFinite(payload.t_llegada)||payload.t_llegada<=0||!Number.isFinite(payload.t_atencion)||payload.t_atencion<=0){
      throw Error("Los tiempos de llegada y servicio deben ser positivos.");
    }
    const response=await fetch("/api/model/",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-CSRFToken":csrf()},body:JSON.stringify(payload)});
    const d=await response.json();
    if(!response.ok||!d.ok)throw Error(d.error||"No se pudo calcular el modelo.");
    if(d.progress){const level=document.getElementById("top-user-level"),xp=document.getElementById("top-user-xp"),coins=document.getElementById("top-user-coins");if(level)level.textContent=d.progress.level;if(xp)xp.textContent=d.progress.xp;if(coins)coins.textContent=d.progress.coins;}
    const a=d.analytic;
    const meets=!!a.stable && a.wq_min!=null && a.wq_min<=10;
    get("lab-result").textContent=(meets?"★ Mini-reto logrado: estable y Wq ≤ 10 minutos. ":a.stable?"Sistema estable, pero todavía no se cumple la meta de espera. ":"Sistema inestable para este modelo. ")
      +"Modifica los parámetros y vuelve a calcular.";
    const values=[
      ["Modelo",a.model],["Estado",a.stable?"Estable":"Inestable"],
      ["Utilización",percent(a.rho)],["Espera Wq",a.wq_min==null?"No finita":format(a.wq_min)+" min"],
      ["Clientes Lq",format(a.lq)],["Espera probable",percent(a.p_wait)],
      ["Bloqueo",percent(a.p_block)],["Capacidad K",a.capacity==null?"Sin límite":a.capacity]
    ];
    get("lab-kpis").innerHTML=values.map(([name,value])=>"<div class='arena-kpi'><small>"+name+"</small><b>"+String(value)+"</b></div>").join("");
    let series=d.simulation?.queue_series||null;
    let title="Evolución de la cola · primera réplica";
    if(d.sequence && !series){
      series=d.sequence.map(row=>({t:row["Llegada (min)"],q:row["Espera (min)"]}));
      title="Espera individual D/D/1";
    }
    const plot=get("lab-plot");
    if(window.Plotly && series?.length){
      window.Plotly.react(plot,[{
        x:series.map(x=>x.t),
        y:series.map(x=>x.q),
        mode:"lines",type:"scatter",line:{color:"#1680a6",width:2,shape:"hv"},
        name:"Magnitud observada"
      }],{
        title:{text:title,font:{size:13}},
        margin:{t:44,b:46,l:50,r:12},
        paper_bgcolor:"#fff",plot_bgcolor:"#fff",
        xaxis:{title:"Tiempo (min)",gridcolor:"#e2edf3"},
        yaxis:{title:d.sequence&&!d.simulation?"Espera (min)":"Clientes en cola",gridcolor:"#e2edf3"}
      },{displayModeBar:false,responsive:true});
    }else if(window.Plotly){window.Plotly.purge(plot);}
    get("lab-model-note").textContent=d.note||"Gráfico observado en horizonte finito; los resultados analíticos pueden corresponder a estado estacionario.";
  }catch(error){
    get("lab-result").textContent="Error: "+error.message;
    get("lab-kpis").replaceChildren();
  }finally{button.disabled=false;}
}
get("lab-run").addEventListener("click",run);
})();
