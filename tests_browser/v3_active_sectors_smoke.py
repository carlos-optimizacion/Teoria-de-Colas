"""Chromium: verify native WebGL scenes and terminology for four active sectors."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

SECTORS=[
    ("banco","Banca","BANCO","Ventanillas activas","financial-branch","teller-window"),
    ("hospital","Salud","HOSPITAL","Boxes activos","emergency-department","clinical-box"),
    ("supermercado","Retail","SUPERMERCADO","Cajas activas","grocery-checkout","checkout-lane"),
    ("logistica","Logística","CENTRO LOGÍSTICO","Andenes activos","industrial-truck-yard","loading-dock"),
]
Path("visual-artifacts").mkdir(exist_ok=True)

with sync_playwright() as p:
    browser=p.chromium.launch(
        headless=True,
        args=["--use-gl=angle","--use-angle=swiftshader","--enable-webgl"],
    )
    page=browser.new_page(viewport={"width":1450,"height":950})
    page.goto("http://127.0.0.1:8501",wait_until="domcontentloaded",timeout=60000)
    for key,label,title,resource,environment,station in SECTORS:
        page.get_by_text("1 · Ingreso de datos y modelo matemático").wait_for(timeout=45000)
        combo=page.get_by_role("combobox",name="Escenario operativo")
        combo.click()
        page.get_by_role("option",name=label,exact=True).click()
        # Validar infraestructura multi-servidor, no solo la instancia D/D/1.
        model=page.get_by_role("combobox",name="Modelo matemático")
        model.click()
        page.get_by_role("option",name="D/D/c",exact=True).click()
        page.get_by_role("button",name="Guardar y validar configuración").click()
        page.get_by_text("2 · Vista previa: entorno construido sin movimiento").wait_for(timeout=90000)
        inner=page.frame_locator("iframe").first
        inner.locator("canvas").wait_for(timeout=60000)
        assert title in inner.locator(".brand b").inner_text(),f"Escena equivocada: {key}"
        assert resource in inner.locator("#stat-active").locator("..").inner_text(),f"Terminología errónea: {key}"
        assert inner.locator("canvas").evaluate("(el)=>el.width>0&&el.height>0"),key
        stage=inner.locator("#stage")
        assert stage.get_attribute("data-sector")==key
        assert stage.get_attribute("data-environment")==environment,(key,stage.get_attribute("data-environment"))
        assert stage.get_attribute("data-station-type")==station,(key,stage.get_attribute("data-station-type"))
        assert int(stage.get_attribute("data-stations"))==4,(key,stage.get_attribute("data-stations"))
        assert inner.locator("#loading").count()==0,f"Escena 3D no terminó de cargar: {key}"
        quality=inner.locator("#quality")
        assert quality.count()==1,key
        assert stage.get_attribute("data-quality-mode")=="auto",key
        assert stage.get_attribute("data-visual-quality") in ("high","balanced"),key
        quality.select_option("high")
        high_scale=float(stage.get_attribute("data-render-scale"))
        assert high_scale>=1.3,key
        assert stage.get_attribute("data-visual-quality")=="high",key
        assert stage.get_attribute("data-shadow-resolution")=="2048",key
        quality.select_option("economy")
        eco_scale=float(stage.get_attribute("data-render-scale"))
        assert high_scale>eco_scale,(key,high_scale,eco_scale)
        assert stage.get_attribute("data-visual-quality")=="economy",key
        assert stage.get_attribute("data-shadow-resolution")=="512",key
        assert inner.locator("canvas").evaluate("(el)=>el.width>0&&el.height>0"),key
        quality.select_option("auto")
        features=json.loads(stage.get_attribute("data-features"))
        if key=="banco":
            assert features["seats"]>=3 and features["racks"]==0
        elif key=="hospital":
            assert features["triage"]>=1 and features["seats"]>=6
        elif key=="supermercado":
            assert features["racks"]>=6 and features["checkoutDecor"]>=1
        elif key=="logistica":
            assert features["forklift"]==1 and features["seats"]==0 and features["racks"]==0
        assert page.get_by_text("2 · Vista previa: entorno construido sin movimiento").is_visible()
        page.screenshot(path=f"visual-artifacts/v3-{key}-preview.png",full_page=True)
        page.get_by_role("button",name="← Volver a ingresar datos").click()
    print("E2E PASS: cuatro ambientes y puestos distintos, WebGL activo, sin mobiliario bancario en logística")
    browser.close()
