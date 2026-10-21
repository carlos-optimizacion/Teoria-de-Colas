from streamlit_sector_scenes import SECTOR_UI, configured_units, render_sector_scene

BASE_FRAME={"t":0,"kind":"start","client":None,"queue":0,"queue_ids":[],"busy":0,"arrivals":0,"completed":0,"blocked":0}

def frame(active,total=8):
    return {**BASE_FRAME,"active":active,"servers":[None]*total}

def test_sector_semantics_are_distinct():
    assert SECTOR_UI["banco"]["service"]=="Ventanillas"
    assert SECTOR_UI["hospital"]["service"]=="Boxes de atención"
    assert SECTOR_UI["supermercado"]["service"]=="Cajas"
    assert SECTOR_UI["fabrica"]["service"]=="Estaciones de inspección"
    assert SECTOR_UI["logistica"]["service"]=="Andenes"
    assert len({SECTOR_UI[k]["service"] for k in SECTOR_UI})==5

def test_each_sector_renders_exact_configured_capacity():
    for key in SECTOR_UI:
        for count in range(1,6):
            f=frame(count,8)
            assert configured_units(f)==count
            html=render_sector_scene(key,f,"ready")
            assert f"<strong>{count}</strong>" in html
            unit=SECTOR_UI[key]["unit_singular"].title()
            for i in range(1,count+1):
                assert f"{unit} {i}" in html
            assert f"{unit} {count+1}" not in html

def test_sector_flow_labels_match_real_process():
    expected={
        "banco":("Ingreso / turnero","Sala de espera","Ventanillas","Salida"),
        "hospital":("Admisión / triaje","Sala de espera","Boxes de atención","Alta / salida"),
        "supermercado":("Zona de compra","Fila de pago","Cajas","Pago / salida"),
        "fabrica":("Ingreso de unidades","Buffer de inspección","Estaciones de inspección","Aprobado / salida"),
        "logistica":("Ingreso de camiones","Patio de espera","Andenes","Despacho / salida"),
    }
    for key,labels in expected.items():
        html=render_sector_scene(key,frame(2),"ready")
        for label in labels:
            assert label in html


def test_rendered_scene_has_no_markdown_code_indentation():
    for key in SECTOR_UI:
        html=render_sector_scene(key,frame(2),"ready")
        first_nonempty=next(line for line in html.splitlines() if line.strip())
        assert first_nonempty.startswith("<div class=\"sector-scene"), first_nonempty
        assert not first_nonempty.startswith("    ")
        assert all(not line.startswith("    ") for line in html.splitlines() if line.strip()), html
        assert "<div class=\"scene-decor" in html
