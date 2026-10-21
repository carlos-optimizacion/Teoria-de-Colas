"""Sector-specific visual semantics and HTML rendering for Decision Lab Streamlit."""
from html import escape
from streamlit_visual_logic import station_descriptors

SECTOR_UI = {
    "banco": {
        "title": "Banco",
        "arrival": "Ingreso / turnero",
        "queue": "Sala de espera",
        "service": "Ventanillas",
        "unit_singular": "ventanilla",
        "unit_plural": "ventanillas",
        "exit": "Salida",
        "icon": "🏦",
        "unit_icon": "▤",
        "person": "cliente",
    },
    "hospital": {
        "title": "Hospital",
        "arrival": "Admisión / triaje",
        "queue": "Sala de espera",
        "service": "Boxes de atención",
        "unit_singular": "box",
        "unit_plural": "boxes",
        "exit": "Alta / salida",
        "icon": "✚",
        "unit_icon": "✚",
        "person": "paciente",
    },
    "supermercado": {
        "title": "Supermercado",
        "arrival": "Zona de compra",
        "queue": "Fila de pago",
        "service": "Cajas",
        "unit_singular": "caja",
        "unit_plural": "cajas",
        "exit": "Pago / salida",
        "icon": "🛒",
        "unit_icon": "▣",
        "person": "cliente",
    },
    "fabrica": {
        "title": "Fábrica",
        "arrival": "Ingreso de unidades",
        "queue": "Buffer de inspección",
        "service": "Estaciones de inspección",
        "unit_singular": "estación",
        "unit_plural": "estaciones",
        "exit": "Aprobado / salida",
        "icon": "⚙",
        "unit_icon": "⌁",
        "person": "unidad",
    },
    "logistica": {
        "title": "Logística",
        "arrival": "Ingreso de camiones",
        "queue": "Patio de espera",
        "service": "Andenes",
        "unit_singular": "andén",
        "unit_plural": "andenes",
        "exit": "Despacho / salida",
        "icon": "🚚",
        "unit_icon": "▥",
        "person": "camión",
    },
}

def _people(ids, kind):
    if not ids:
        return '<span class="empty-state">Sin elementos en espera</span>'
    icon = {"fabrica":"◆","logistica":"▰"}.get(kind,"●")
    return "".join(
        f'<span class="sector-person sector-person-{kind}" title="ID {escape(str(cid))}"><i>{icon}</i><em>{escape(str(cid))}</em></span>'
        for cid in ids[:16]
    )

def render_sector_scene(scenario_key, frame, status):
    ui=SECTOR_UI[scenario_key]
    active=max(0,int(frame.get("active",0) or 0))
    busy=int(frame.get("busy",0) or 0)
    queue_ids=list(frame.get("queue_ids") or [])
    stations=[]
    for item in station_descriptors(frame):
        n=item["number"]; cid=item["client"]; draining=item["draining"]
        if draining:
            state="closing";label="CIERRE PENDIENTE";body=f'<span class="sector-person serving"><i>●</i><em>{escape(str(cid))}</em></span>'
        elif cid is not None:
            state="busy";label="ATENDIENDO";body=f'<span class="sector-person serving"><i>●</i><em>{escape(str(cid))}</em></span>'
        else:
            state="free";label="LIBRE";body=f'<span class="sector-unit-symbol">{ui["unit_icon"]}</span>'
        stations.append(
            f'<div class="sector-unit {scenario_key} {state}" data-configured="{str(item["configured"]).lower()}">'
            f'<span class="sector-unit-name">{escape(ui["unit_singular"].title())} {n}</span>{body}<small>{label}</small></div>'
        )
    count_label = ui["unit_singular"] if active==1 else ui["unit_plural"]
    queue_count=int(frame.get("queue",0) or 0)
    status_label={"ready":"ESCENARIO CONSTRUIDO","running":"SIMULACIÓN EN CURSO","paused":"SIMULACIÓN PAUSADA","finished":"JORNADA FINALIZADA"}.get(status,status.upper())
    arrival_client=frame.get("client") if frame.get("kind")=="arrival" else None
    departure_client=frame.get("client") if frame.get("kind")=="departure" else None
    incoming=(f'<span class="sector-person moving-in"><i>●</i><em>{arrival_client}</em></span>' if arrival_client else '<span class="empty-state">—</span>')
    outgoing=(f'<span class="sector-person moving-out"><i>●</i><em>{departure_client}</em></span>' if departure_client else '<span class="empty-state">—</span>')
    return f"""
    <div class="sector-scene sector-{scenario_key}">
      <div class="sector-scene-head">
        <div><span class="sector-big-icon">{ui["icon"]}</span><b>{ui["title"]}</b><small>{status_label}</small></div>
        <div class="sector-capacity"><small>CAPACIDAD OPERATIVA</small><strong>{active}</strong><span>{count_label}</span></div>
      </div>
      <div class="sector-flow">
        <div class="sector-zone arrival-zone"><span class="zone-kicker">01</span><b>{ui["arrival"]}</b><small>{frame.get("arrivals",0)} llegadas acumuladas</small><div class="sector-slot">{incoming}</div></div>
        <div class="sector-arrow">→</div>
        <div class="sector-zone queue-zone"><span class="zone-kicker">02</span><b>{ui["queue"]}</b><small>{queue_count} esperando</small><div class="sector-people-row">{_people(queue_ids,scenario_key)}</div></div>
        <div class="sector-arrow">→</div>
        <div class="sector-zone service-zone"><span class="zone-kicker">03</span><b>{ui["service"]}</b><small>{busy} ocupados · {active} activos</small><div class="sector-units">{''.join(stations)}</div></div>
        <div class="sector-arrow">→</div>
        <div class="sector-zone exit-zone"><span class="zone-kicker">04</span><b>{ui["exit"]}</b><small>{frame.get("completed",0)} completados</small><div class="sector-slot">{outgoing}</div></div>
      </div>
    </div>
    """

def configured_units(frame):
    return sum(1 for x in station_descriptors(frame) if x["configured"])
