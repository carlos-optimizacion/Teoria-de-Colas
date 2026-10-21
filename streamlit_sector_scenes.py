"""Sector-specific high-definition visual scenes for Decision Lab Streamlit."""
from html import escape
from textwrap import dedent
from streamlit_visual_logic import station_descriptors

SECTOR_UI = {
    "banco": dict(title="Banco",arrival="Ingreso / turnero",queue="Sala de espera",service="Ventanillas",
                  unit_singular="ventanilla",unit_plural="ventanillas",exit="Salida",icon="🏦",person="cliente"),
    "hospital": dict(title="Hospital",arrival="Admisión / triaje",queue="Sala de espera",service="Boxes de atención",
                     unit_singular="box",unit_plural="boxes",exit="Alta / salida",icon="✚",person="paciente"),
    "supermercado": dict(title="Supermercado",arrival="Zona de compra",queue="Fila de pago",service="Cajas",
                         unit_singular="caja",unit_plural="cajas",exit="Pago / salida",icon="🛒",person="cliente"),
    "fabrica": dict(title="Fábrica",arrival="Ingreso de unidades",queue="Buffer de inspección",service="Estaciones de inspección",
                    unit_singular="estación",unit_plural="estaciones",exit="Aprobado / salida",icon="⚙",person="unidad"),
    "logistica": dict(title="Logística",arrival="Ingreso de camiones",queue="Patio de espera",service="Andenes",
                      unit_singular="andén",unit_plural="andenes",exit="Despacho / salida",icon="🚚",person="camión"),
}

def _unit_visual(key):
    if key=="banco":
        return '<div class="bank-window"><span>VENTANILLA</span><i></i></div>'
    if key=="hospital":
        return '<div class="hospital-box"><span>BOX</span><i>+</i></div>'
    if key=="supermercado":
        return '<div class="checkout-lane"><i></i><span>CAJA</span></div>'
    if key=="fabrica":
        return '<div class="inspection-station"><i>⌁</i><span>QC</span></div>'
    return '<div class="loading-dock"><i></i><span>ANDÉN</span></div>'

def _people(ids, kind):
    if not ids:
        return '<span class="empty-state">Sin elementos en espera</span>'
    icon={"fabrica":"◆","logistica":"▰"}.get(kind,"●")
    return "".join(
        f'<span class="sector-person sector-person-{kind}" title="ID {escape(str(cid))}"><i>{icon}</i><em>{escape(str(cid))}</em></span>'
        for cid in ids[:18]
    )

def _decor(key):
    if key=="banco":
        return """
        <div class="scene-decor bank-decor">
          <div class="bank-sign">BANCO</div><div class="ticket-kiosk">TURNO<br><b>A-01</b></div>
          <div class="chair-row"><i></i><i></i><i></i><i></i></div><div class="digital-board">TURNO &nbsp; VENTANILLA</div>
        </div>"""
    if key=="hospital":
        return """
        <div class="scene-decor hospital-decor">
          <div class="triage-desk">TRIAJE</div><div class="medical-cross">+</div>
          <div class="chair-row"><i></i><i></i><i></i><i></i></div><div class="hospital-corridor"></div>
        </div>"""
    if key=="supermercado":
        return """
        <div class="scene-decor market-decor">
          <div class="aisle"><i></i><i></i><i></i></div><div class="cart-icon">🛒</div>
          <div class="queue-rail"></div><div class="market-sign">ZONA DE CAJAS</div>
        </div>"""
    if key=="fabrica":
        return """
        <div class="scene-decor factory-decor">
          <div class="conveyor"><i></i><i></i><i></i><i></i><i></i></div><div class="qc-sign">CONTROL DE CALIDAD</div>
          <div class="safety-line"></div><div class="factory-light">●</div>
        </div>"""
    return """
    <div class="scene-decor logistics-decor">
      <div class="gate-house">PORTERÍA</div><div class="yard-lanes"><i></i><i></i><i></i></div>
      <div class="truck-shape"><i></i></div><div class="dock-sign">PATIO / ANDENES</div>
    </div>"""

def render_sector_scene(scenario_key, frame, status, background_uri=''):
    ui=SECTOR_UI[scenario_key]
    event_kind=str(frame.get("kind") or "start")
    active=max(0,int(frame.get("active",0) or 0))
    busy=int(frame.get("busy",0) or 0)
    queue_ids=list(frame.get("queue_ids") or [])
    stations=[]
    for item in station_descriptors(frame):
        n=item["number"];cid=item["client"];draining=item["draining"]
        if draining:
            state="closing";label="CIERRE PENDIENTE";client=f'<span class="sector-person serving"><i>●</i><em>{escape(str(cid))}</em></span>'
        elif cid is not None:
            state="busy";label="ATENDIENDO";client=f'<span class="sector-person serving"><i>●</i><em>{escape(str(cid))}</em></span>'
        else:
            state="free";label="LIBRE";client=""
        stations.append(
            f'<div class="sector-unit {scenario_key} {state}" data-configured="{str(item["configured"]).lower()}">'
            f'<span class="sector-unit-name">{escape(ui["unit_singular"].title())} {n}</span>{_unit_visual(scenario_key)}{client}<small>{label}</small></div>'
        )
    count_label=ui["unit_singular"] if active==1 else ui["unit_plural"]
    status_label={"ready":"ESCENARIO CONSTRUIDO","running":"SIMULACIÓN EN CURSO","paused":"SIMULACIÓN PAUSADA","finished":"JORNADA FINALIZADA"}.get(status,status.upper())
    arrival_client=frame.get("client") if frame.get("kind")=="arrival" else None
    departure_client=frame.get("client") if frame.get("kind")=="departure" else None
    incoming=f'<span class="sector-person moving-in"><i>●</i><em>{arrival_client}</em></span>' if arrival_client else '<span class="empty-state">—</span>'
    outgoing=f'<span class="sector-person moving-out"><i>●</i><em>{departure_client}</em></span>' if departure_client else '<span class="empty-state">—</span>'
    html=dedent(f"""
    <div class="sector-scene sector-{scenario_key} event-{event_kind}">
      <div class="sector-scene-head">
        <div class="sector-title"><span class="sector-big-icon">{ui["icon"]}</span><b>{ui["title"]}</b><small>{status_label}</small></div>
        <div class="live-event"><span></span><b>{escape(event_kind.upper())}</b></div>
        <div class="sector-capacity"><small>CAPACIDAD OPERATIVA</small><strong>{active}</strong><span>{count_label}</span></div>
      </div>
      <div class="sector-stage">
        <div class="sector-art"{f' style="background-image:url({background_uri})"' if background_uri else ''}></div>
        {_decor(scenario_key)}
        <div class="sector-flow">
          <div class="sector-zone arrival-zone"><span class="zone-kicker">01</span><b>{ui["arrival"]}</b><small>{frame.get("arrivals",0)} llegadas acumuladas</small><div class="sector-slot">{incoming}</div></div>
          <div class="sector-arrow">→</div>
          <div class="sector-zone queue-zone"><span class="zone-kicker">02</span><b>{ui["queue"]}</b><small>{frame.get("queue",0)} esperando</small><div class="sector-people-row">{_people(queue_ids,scenario_key)}</div></div>
          <div class="sector-arrow">→</div>
          <div class="sector-zone service-zone"><span class="zone-kicker">03</span><b>{ui["service"]}</b><small>{busy} ocupados · {active} activos</small><div class="sector-units">{''.join(stations)}</div></div>
          <div class="sector-arrow">→</div>
          <div class="sector-zone exit-zone"><span class="zone-kicker">04</span><b>{ui["exit"]}</b><small>{frame.get("completed",0)} completados</small><div class="sector-slot">{outgoing}</div></div>
        </div>
      </div>
    </div>
    """)
    return "\n".join(line.lstrip() for line in html.splitlines() if line.strip())

def configured_units(frame):
    return sum(1 for x in station_descriptors(frame) if x["configured"])
