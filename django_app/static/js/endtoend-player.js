(() => {
  const state = {
    data: null,
    time: 0,
    speed: 1,
    running: false,
    lastWall: null,
    raf: null,
    view: 'compare',
    indexes: {current: 0, recommended: 0},
    rendered: {current: -1, recommended: -1},
  };

  const el = id => document.getElementById(id);
  const fmtClock = minutes => {
    const totalSeconds = Math.max(0, Math.round(minutes * 60));
    const mm = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
    const ss = String(totalSeconds % 60).padStart(2, '0');
    return `${mm}:${ss}`;
  };
  const pct = x => `${(Number(x || 0) * 100).toFixed(1)}%`;
  const num = (x, d = 2) => Number(x || 0).toFixed(d);

  function person(customer, waiting = false) {
    return `<div class="person ${waiting ? 'waiting' : ''}" title="Cliente ${customer}"><span class="person-id">${customer}</span></div>`;
  }

  function eventText(frame) {
    if (!frame) return 'Preparando simulación.';
    if (frame.kind === 'start') return 'Sistema listo para iniciar la simulación.';
    if (frame.kind === 'end') return 'Fin del horizonte simulado.';
    if (frame.kind === 'arrival_queue') return `Cliente ${frame.customer} llega y se incorpora a la cola porque todos los servidores están ocupados.`;
    if (frame.kind === 'arrival_service') return `Cliente ${frame.customer} llega y pasa directamente al servidor ${frame.server}.`;
    if (frame.kind === 'departure' && frame.started_customer) return `Cliente ${frame.customer} termina su atención en el servidor ${frame.server}; el cliente ${frame.started_customer} sale de la cola e inicia servicio.`;
    if (frame.kind === 'departure') return `Cliente ${frame.customer} termina su atención en el servidor ${frame.server}, que queda disponible.`;
    return 'Evento de simulación.';
  }

  function boardHtml(label, sim, frame) {
    const queue = frame?.queue || [];
    const servers = frame?.servers || Array(sim.servers_count).fill(null);
    const visibleQueue = queue.slice(0, 16);
    const hiddenQueue = Math.max(0, queue.length - visibleQueue.length);
    return `
      <div class="sim-board-head">
        <div><div class="sim-scenario-label">${label}</div><b>M/M/${sim.servers_count}</b><span>${sim.servers_count} servidor(es) · horizonte ${sim.horizon_min} min</span></div>
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

  function renderSummary() {
    const current = state.data.current;
    const recommended = state.data.recommended;
    el('sim-summary-grid').innerHTML = [
      ['Actual · máx. cola', current.max_queue],
      ['Propuesto · máx. cola', recommended.max_queue],
      ['Actual · Lq sim.', num(current.avg_queue)],
      ['Propuesto · Lq sim.', num(recommended.avg_queue)],
      ['Actual · utilización', pct(current.utilization)],
      ['Propuesto · utilización', pct(recommended.utilization)],
    ].map(([label, value]) => `<div class="sim-summary-card"><b>${value}</b><span>${label}</span></div>`).join('');
    el('sim-note').textContent = state.data.note || '';
  }

  function latestFrame(which) {
    const sim = state.data[which];
    let idx = state.indexes[which];
    while (idx + 1 < sim.frames.length && sim.frames[idx + 1].time <= state.time) idx += 1;
    state.indexes[which] = idx;
    return {frame: sim.frames[idx], idx};
  }

  function renderScenario(which, label) {
    const found = latestFrame(which);
    if (state.rendered[which] === found.idx) return;
    state.rendered[which] = found.idx;
    el(`sim-board-${which}`).innerHTML = boardHtml(label, state.data[which], found.frame);
  }

  function updateClock() {
    const horizon = state.data?.horizon_min || 60;
    el('sim-clock').textContent = `${fmtClock(state.time)} / ${fmtClock(horizon)}`;
    el('sim-progress-bar').style.width = `${Math.min(100, (state.time / horizon) * 100)}%`;
  }

  function renderAll(force = false) {
    if (!state.data) return;
    if (force) state.rendered = {current: -1, recommended: -1};
    renderScenario('current', 'ESCENARIO ACTUAL');
    renderScenario('recommended', 'ALTERNATIVA RECOMENDADA');
    updateClock();
  }

  function pause() {
    state.running = false;
    state.lastWall = null;
    if (state.raf) cancelAnimationFrame(state.raf);
    state.raf = null;
    if (el('sim-play')) el('sim-play').textContent = state.time >= (state.data?.horizon_min || 0) ? '▶ Repetir' : '▶ Continuar';
  }

  function restart(autoplay = false) {
    if (!state.data) return;
    state.time = 0;
    state.indexes = {current: 0, recommended: 0};
    state.rendered = {current: -1, recommended: -1};
    state.lastWall = null;
    renderAll(true);
    if (autoplay) play(); else {
      state.running = false;
      el('sim-play').textContent = '▶ Iniciar';
    }
  }

  function tick(now) {
    if (!state.running || !state.data) return;
    if (state.lastWall == null) state.lastWall = now;
    const elapsedSeconds = Math.max(0, (now - state.lastWall) / 1000);
    state.lastWall = now;
    state.time = Math.min(state.data.horizon_min, state.time + elapsedSeconds * state.speed);
    renderAll();
    if (state.time >= state.data.horizon_min) {
      pause();
      return;
    }
    state.raf = requestAnimationFrame(tick);
  }

  function play() {
    if (!state.data) return;
    if (state.time >= state.data.horizon_min) restart(false);
    if (state.running) {
      pause();
      return;
    }
    state.running = true;
    state.lastWall = null;
    el('sim-play').textContent = '⏸ Pausa';
    state.raf = requestAnimationFrame(tick);
  }

  function setView(view) {
    state.view = view;
    document.querySelectorAll('.sim-chip').forEach(btn => btn.classList.toggle('active', btn.dataset.view === view));
    const comparison = el('sim-comparison');
    comparison.classList.remove('single-current', 'single-recommended');
    if (view === 'current') comparison.classList.add('single-current');
    if (view === 'recommended') comparison.classList.add('single-recommended');
  }

  function bindControls() {
    el('sim-play')?.addEventListener('click', play);
    el('sim-restart')?.addEventListener('click', () => restart(false));
    el('sim-speed')?.addEventListener('change', e => { state.speed = Number(e.target.value) || 1; });
    document.querySelectorAll('.sim-chip').forEach(btn => btn.addEventListener('click', () => setView(btn.dataset.view)));
  }

  window.DecisionLabVisual = {
    load(data) {
      if (!data || !data.current || !data.recommended) return;
      pause();
      state.data = data;
      state.speed = Number(el('sim-speed')?.value || 1);
      el('visual-simulation-panel').hidden = false;
      renderSummary();
      setView('compare');
      restart(false);
    },
  };

  bindControls();
})();
