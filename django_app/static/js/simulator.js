(() => {
  const form = document.getElementById('simulator-form');
  const el = id => document.getElementById(id);
  const number = id => Number(el(id).value);
  const pct = value => value == null ? '—' : `${(Number(value) * 100).toFixed(1)}%`;
  const num = (value, digits = 2) => value == null || !Number.isFinite(Number(value)) ? '—' : Number(value).toFixed(digits);
  const csrf = () => document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';

  const player = {
    data: null,
    time: 0,
    speed: 1,
    running: false,
    lastWall: null,
    frameIndex: 0,
    renderedIndex: -1,
    raf: null,
  };

  function payload() {
    return {
      t_llegada: number('sim-arrival'),
      t_atencion: number('sim-service'),
      servers: number('sim-servers'),
      horizon: number('sim-horizon'),
      sla_threshold: number('sim-sla-threshold'),
      sla_target: number('sim-sla-target'),
      seed: 2026,
    };
  }

  function statusCard(status) {
    return `<div class="simulator-status ${status.tone || ''}"><b>${status.title}</b><span>${status.message}</span></div>`;
  }

  function renderKpis(a) {
    const cards = [
      ['ρ', pct(a.rho), 'Utilización de la capacidad'],
      ['Wq', `${num(a.wq_min)} min`, 'Espera promedio en cola'],
      ['Lq', num(a.lq), 'Clientes promedio esperando'],
      ['P(espera)', pct(a.p_wait), 'Probabilidad de tener que esperar'],
      ['NS', pct(a.service_level), `P(Wq ≤ ${num(a.sla_threshold, 1)} min)`],
      ['W', `${num(a.w_min)} min`, 'Tiempo promedio total en el sistema'],
      ['λe', `${num(a.effective_rate)} /h`, 'Tasa efectiva del escenario'],
      ['Estado', a.stable ? 'Estable' : 'Inestable', a.stable ? 'Existe estado estacionario' : 'La cola no converge en promedio'],
    ];
    el('simulator-kpis').innerHTML = cards.map(([symbol, value, label]) => `
      <article class="simulator-kpi"><span class="kpi-symbol">${symbol}</span><b>${value}</b><span>${label}</span></article>
    `).join('');
  }

  function renderHelp(items) {
    el('indicator-help').innerHTML = items.map(item => `
      <article class="indicator-help-card">
        <div class="indicator-help-symbol">${item.symbol}</div>
        <div><b>${item.name}</b><p>${item.definition}</p><small>${item.reading}</small></div>
      </article>
    `).join('');
  }

  function cleanLayout(xTitle, yTitle, extra = {}) {
    return {
      margin: {l: 52, r: 18, t: 10, b: 48},
      paper_bgcolor: '#FFFFFF',
      plot_bgcolor: '#FFFFFF',
      showlegend: false,
      font: {family: 'Inter, system-ui, sans-serif', size: 12, color: '#667085'},
      xaxis: {title: {text: xTitle, font: {size: 11}}, gridcolor: '#EEF2F6', zeroline: false, linecolor: '#DDE5EC'},
      yaxis: {title: {text: yTitle, font: {size: 11}}, gridcolor: '#EEF2F6', zeroline: false, linecolor: '#DDE5EC', rangemode: 'tozero'},
      hoverlabel: {bordercolor: '#DDE5EC', font: {size: 12}},
      ...extra,
    };
  }

  function renderCharts(a, visual) {
    const frames = visual.frames || [];
    const times = frames.map(f => f.time);
    const queues = frames.map(f => f.queue_length || 0);
    Plotly.react('sim-queue-chart', [{x: times, y: queues, type: 'scatter', mode: 'lines', line: {width: 3, shape: 'hv'}, hovertemplate: 't = %{x:.1f} min<br>Cola = %{y}<extra></extra>'}], cleanLayout('Tiempo simulado (min)', 'Clientes en cola'), {responsive: true, displayModeBar: false});

    const labels = ['Utilización', 'P(espera)', 'Nivel de servicio'];
    const values = [(a.rho || 0) * 100, (a.p_wait || 0) * 100, (a.service_level || 0) * 100];
    Plotly.react('sim-service-chart', [{x: values, y: labels, type: 'bar', orientation: 'h', marker: {color: '#2A78A8'}, hovertemplate: '%{y}: %{x:.1f}%<extra></extra>'}], cleanLayout('Porcentaje', '', {xaxis: {title: {text: 'Porcentaje', font: {size: 11}}, range: [0, 100], gridcolor: '#EEF2F6', zeroline: false, linecolor: '#DDE5EC'}, yaxis: {gridcolor: '#FFFFFF', zeroline: false, linecolor: '#FFFFFF'}}), {responsive: true, displayModeBar: false});
  }

  function fmtClock(minutes) {
    const totalSeconds = Math.max(0, Math.round(minutes * 60));
    const mm = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
    const ss = String(totalSeconds % 60).padStart(2, '0');
    return `${mm}:${ss}`;
  }

  function person(customer, waiting = false) {
    return `<div class="person ${waiting ? 'waiting' : ''}" title="Cliente ${customer}"><span class="person-id">${customer}</span></div>`;
  }

  function eventText(frame) {
    if (!frame) return 'Sistema listo.';
    if (frame.kind === 'start') return 'Sistema listo para iniciar la simulación.';
    if (frame.kind === 'end') return 'Fin del horizonte simulado.';
    if (frame.kind === 'arrival_queue') return `Cliente ${frame.customer} llega y se incorpora a la cola porque todos los servidores están ocupados.`;
    if (frame.kind === 'arrival_service') return `Cliente ${frame.customer} llega y pasa directamente al servidor ${frame.server}.`;
    if (frame.kind === 'departure' && frame.started_customer) return `Cliente ${frame.customer} termina su atención; el cliente ${frame.started_customer} sale de la cola e inicia servicio en el servidor ${frame.server}.`;
    if (frame.kind === 'departure') return `Cliente ${frame.customer} termina su atención y el servidor ${frame.server} queda disponible.`;
    return 'Evento de simulación.';
  }

  function boardHtml(sim, frame) {
    const queue = frame?.queue || [];
    const servers = frame?.servers || Array(sim.servers_count).fill(null);
    const visibleQueue = queue.slice(0, 18);
    const hiddenQueue = Math.max(0, queue.length - visibleQueue.length);
    const modelName = sim.servers_count === 1 ? 'M/M/1' : `M/M/${sim.servers_count}`;
    return `
      <div class="sim-board-head">
        <div><div class="sim-scenario-label">ESCENARIO DEL ALUMNO</div><b>${modelName}</b><span>${sim.servers_count} servidor(es) · horizonte ${sim.horizon_min} min</span></div>
        <div class="sim-live">t = ${fmtClock(frame?.time || 0)}</div>
      </div>
      <div class="sim-kpis">
        <div class="sim-kpi"><b>${frame?.arrivals || 0}</b><small>Llegadas</small></div>
        <div class="sim-kpi"><b>${frame?.completed || 0}</b><small>Atendidos</small></div>
        <div class="sim-kpi"><b>${frame?.queue_length || 0}</b><small>En cola</small></div>
        <div class="sim-kpi"><b>${frame?.max_queue || 0}</b><small>Máx. cola</small></div>
      </div>
      <div class="sim-flow">
        <div class="sim-zone sim-entry"><div class="sim-zone-title">Llegadas</div><div class="sim-arrow">→</div><small>Clientes</small></div>
        <div class="sim-zone"><div class="sim-zone-title">Cola FIFO</div><div class="sim-queue">${visibleQueue.map(c => person(c, true)).join('')}${hiddenQueue ? `<span class="empty-server">+${hiddenQueue} más</span>` : ''}${queue.length === 0 ? '<span class="empty-server">Sin clientes esperando</span>' : ''}</div></div>
        <div class="sim-zone"><div class="sim-zone-title">Servidores</div><div class="sim-servers">${servers.map((customer, i) => `<div class="server-slot ${customer ? 'busy' : ''}">${customer ? person(customer) : '<span class="empty-server">Libre</span>'}<span>Servidor ${i + 1}</span></div>`).join('')}</div></div>
        <div class="sim-zone sim-exit"><div class="sim-zone-title">Salida</div><div class="sim-arrow">→</div><small>Atendidos</small></div>
      </div>
      <div class="sim-event">${eventText(frame)}</div>
      ${sim.truncated ? '<div class="sim-truncated">La línea visual fue limitada por seguridad; los indicadores agregados conservan el horizonte completo.</div>' : ''}
    `;
  }

  function renderSummary(sim) {
    const values = [
      ['Máx. cola', sim.max_queue],
      ['Lq de la réplica', num(sim.avg_queue)],
      ['Utilización réplica', pct(sim.utilization)],
      ['Espera de quienes esperaron', `${num(sim.avg_wait_started)} min`],
    ];
    el('sim-summary-grid').innerHTML = values.map(([label, value]) => `<div class="sim-summary-card"><b>${value}</b><span>${label}</span></div>`).join('');
  }

  function latestFrame() {
    const frames = player.data.frames;
    let idx = player.frameIndex;
    while (idx + 1 < frames.length && frames[idx + 1].time <= player.time) idx += 1;
    player.frameIndex = idx;
    return {frame: frames[idx], idx};
  }

  function updateClock() {
    const horizon = player.data?.horizon_min || 60;
    el('sim-clock').textContent = `${fmtClock(player.time)} / ${fmtClock(horizon)}`;
    el('sim-progress-bar').style.width = `${Math.min(100, (player.time / horizon) * 100)}%`;
  }

  function renderPlayer(force = false) {
    if (!player.data) return;
    const found = latestFrame();
    if (force || player.renderedIndex !== found.idx) {
      player.renderedIndex = found.idx;
      el('sim-board').innerHTML = boardHtml(player.data, found.frame);
    }
    updateClock();
  }

  function pause() {
    player.running = false;
    player.lastWall = null;
    if (player.raf) cancelAnimationFrame(player.raf);
    player.raf = null;
    if (el('sim-play')) el('sim-play').textContent = player.time >= (player.data?.horizon_min || 0) ? '▶ Repetir' : '▶ Continuar';
  }

  function restart(autoplay = false) {
    if (!player.data) return;
    player.time = 0;
    player.frameIndex = 0;
    player.renderedIndex = -1;
    player.lastWall = null;
    renderPlayer(true);
    if (autoplay) play(); else {
      player.running = false;
      el('sim-play').textContent = '▶ Iniciar';
    }
  }

  function tick(now) {
    if (!player.running || !player.data) return;
    if (player.lastWall == null) player.lastWall = now;
    const elapsedSeconds = Math.max(0, (now - player.lastWall) / 1000);
    player.lastWall = now;
    player.time = Math.min(player.data.horizon_min, player.time + elapsedSeconds * player.speed);
    renderPlayer();
    if (player.time >= player.data.horizon_min) {
      pause();
      return;
    }
    player.raf = requestAnimationFrame(tick);
  }

  function play() {
    if (!player.data) return;
    if (player.time >= player.data.horizon_min) restart(false);
    if (player.running) {
      pause();
      return;
    }
    player.running = true;
    player.lastWall = null;
    el('sim-play').textContent = '⏸ Pausa';
    player.raf = requestAnimationFrame(tick);
  }

  function loadPlayer(sim) {
    pause();
    player.data = sim;
    player.time = 0;
    player.speed = Number(el('sim-speed').value) || 1;
    player.frameIndex = 0;
    player.renderedIndex = -1;
    renderSummary(sim);
    restart(false);
  }

  async function run(event) {
    if (event) event.preventDefault();
    el('simulator-results').hidden = false;
    el('simulator-alert').innerHTML = '<div class="notice">Calculando escenario y generando réplica…</div>';
    try {
      const response = await fetch('/api/simulator/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()},
        body: JSON.stringify(payload()),
      });
      const data = await response.json();
      if (!data.ok) throw new Error(data.error || 'No se pudo ejecutar el simulador.');
      el('simulator-alert').innerHTML = '<div class="notice success">Escenario actualizado. Cambia un parámetro y vuelve a simular para comparar tu decisión.</div>';
      el('simulator-status').innerHTML = statusCard(data.status);
      renderKpis(data.analytic);
      renderHelp(data.indicator_help || []);
      renderCharts(data.analytic, data.visual);
      loadPlayer(data.visual);
      el('simulator-charts-panel').hidden = false;
      el('simulator-player-panel').hidden = false;
      el('simulator-help-panel').hidden = false;
    } catch (error) {
      el('simulator-alert').innerHTML = `<div class="notice danger">${error.message}</div>`;
    }
  }

  form.addEventListener('submit', run);
  el('sim-play').addEventListener('click', play);
  el('sim-restart').addEventListener('click', () => restart(false));
  el('sim-speed').addEventListener('change', event => { player.speed = Number(event.target.value) || 1; });
  window.addEventListener('DOMContentLoaded', run);
})();
