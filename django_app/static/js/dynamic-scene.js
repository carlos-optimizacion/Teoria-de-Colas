/* Shared event-driven illustrated scene for Challenge and the academic M/M/s player.
 * Environment imagery is decorative. Every rendered post and customer derives
 * from the simulation's capacity and event snapshot, not from a demo animation.
 */
(() => {
  "use strict";
  const sceneInstances = new WeakMap();
  const node = (tag, className, text) => {
    const element = document.createElement(tag);
    element.className = className;
    if (text !== undefined) element.textContent = String(text);
    return element;
  };
  function mount(host) {
    if (!host) return null;
    if (sceneInstances.has(host)) return sceneInstances.get(host);
    const shell = node("div", "dynamic-facility");
    const queue = node("section", "dynamic-queue");
    const qTitle = node("div", "dynamic-zone-heading", "SALA DE ESPERA");
    const qCount = node("strong", "dynamic-zone-count", "0");
    qTitle.appendChild(qCount);
    const queuePlaces = node("div", "dynamic-wait-places");
    queue.append(qTitle, queuePlaces);
    const stations = node("section", "dynamic-service");
    const sTitle = node("div", "dynamic-zone-heading", "PUESTOS OPERATIVOS");
    const sCount = node("strong", "dynamic-zone-count", "0");
    sTitle.appendChild(sCount);
    const stationGrid = node("div", "dynamic-station-grid");
    stations.append(sTitle, stationGrid);
    const layer = node("div", "dynamic-client-layer");
    layer.setAttribute("aria-hidden", "true");
    shell.append(queue, stations, layer);
    host.appendChild(shell);
    let actors = new Map();
    let current = null;
    const boxPosition = (target) => {
      const base = shell.getBoundingClientRect(), box = target.getBoundingClientRect();
      return {x: box.left + box.width / 2 - base.left, y: box.top + box.height / 2 - base.top};
    };
    function update(snapshot) {
      current = snapshot;
      if (!snapshot) return;
      const q = Array.isArray(snapshot.queue_ids) ? snapshot.queue_ids : (snapshot.queue || []);
      const ss = Array.isArray(snapshot.servers) ? snapshot.servers : [];
      const active = Number.isFinite(+snapshot.active) ? Math.max(0, Math.min(ss.length, Number(snapshot.active))) : ss.length;
      const stationsVisible = ss.map((id, index) => ({id, index})).filter(({id, index}) => index < active || id != null);
      const visibleQueue = q.slice(0, 20);
      qCount.textContent = String(snapshot.queue_length ?? (typeof snapshot.queue === "number" ? snapshot.queue : q.length));
      sCount.textContent = stationsVisible.length + " / " + ss.length;
      stationGrid.style.setProperty("--scene-columns", String(Math.max(1, Math.min(4, stationsVisible.length))));
      stationGrid.replaceChildren();
      const anchorById = new Map();
      for (const {id, index} of stationsVisible) {
        const card = node("div", "dynamic-station" + (id != null ? " is-busy" : index < active ? " is-free" : " is-closing"));
        card.dataset.station = String(index + 1);
        card.dataset.state = id != null ? (index < active ? "busy" : "closing") : "free";
        card.append(
          node("span", "dynamic-station-number", "PUESTO " + (index + 1)),
          node("span", "dynamic-station-icon", "▤"),
          node("span", "dynamic-station-state", id != null ? (index < active ? "ATENDIENDO" : "CIERRE PENDIENTE") : "LIBRE")
        );
        const target = node("div", "dynamic-station-target");
        card.appendChild(target);
        stationGrid.appendChild(card);
        if (id != null) anchorById.set(String(id), target);
      }
      queuePlaces.replaceChildren();
      for (const id of visibleQueue) {
        const place = node("div", "dynamic-wait-place");
        place.dataset.customer = String(id);
        queuePlaces.appendChild(place);
        anchorById.set(String(id), place);
      }
      const surplus = (snapshot.queue_length ?? (typeof snapshot.queue === "number" ? snapshot.queue : q.length)) - visibleQueue.length;
      if (surplus > 0) queuePlaces.appendChild(node("div", "dynamic-wait-more", "+" + surplus + " esperando"));
      for (const [id, avatar] of actors) {
        if (!anchorById.has(id)) {
          avatar.remove();
          actors.delete(id);
        }
      }
      for (const [id, anchor] of anchorById) {
        let avatar = actors.get(id);
        const serving = !!anchor.closest(".dynamic-station");
        if (!avatar) {
          avatar = node("span", "scene-avatar " + (serving ? "scene-avatar-serving" : "scene-avatar-wait"), id);
          avatar.dataset.client = id;
          avatar.style.left = "0px";
          avatar.style.top = "65%";
          layer.appendChild(avatar);
          actors.set(id, avatar);
        }
        avatar.className = "scene-avatar " + (serving ? "scene-avatar-serving" : "scene-avatar-wait");
        avatar.title = "Cliente " + id + (serving ? " atendido" : " en cola");
        const {x, y} = boxPosition(anchor);
        avatar.style.left = x + "px";
        avatar.style.top = y + "px";
      }
      shell.dataset.active = String(active);
      shell.dataset.visibleStations = String(stationsVisible.length);
    }
    const handleResize = () => { if (current) update(current); };
    window.addEventListener("resize", handleResize, {passive: true});
    const api = {render: update, getVisibleStations: () => +shell.dataset.visibleStations,
      destroy: () => {window.removeEventListener("resize", handleResize);shell.remove();sceneInstances.delete(host);actors.clear();}};
    sceneInstances.set(host, api);
    return api;
  }
  window.DecisionLabScene = {mount};
})();
