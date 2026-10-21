"""Pure visual rules shared by Streamlit rendering/tests."""

def station_descriptors(frame):
    """Return only stations that should be physically visible.

    Configured stations are indices < active. A station above active remains visible
    only while finishing a customer already in service (draining / cierre pendiente).
    """
    servers=list(frame.get("servers") or [])
    active=max(0,int(frame.get("active",0) or 0))
    visible=[]
    for i,cid in enumerate(servers):
        configured=i<active
        draining=(not configured and cid is not None)
        if not configured and not draining:
            continue
        visible.append({
            "number":i+1,
            "client":cid,
            "configured":configured,
            "draining":draining,
        })
    return visible

def configured_station_count(frame):
    return sum(1 for x in station_descriptors(frame) if x["configured"])
