"""Chromium: verify native WebGL scenes and terminology for four active sectors."""
from pathlib import Path
from playwright.sync_api import sync_playwright

SECTORS=[
    ("banco","Banca","BANCO","Ventanillas activas"),
    ("hospital","Salud","HOSPITAL","Boxes activos"),
    ("supermercado","Retail","SUPERMERCADO","Cajas activas"),
    ("logistica","Logística","CENTRO LOGÍSTICO","Andenes activos"),
]
Path("visual-artifacts").mkdir(exist_ok=True)

with sync_playwright() as p:
    browser=p.chromium.launch(
        headless=True,
        args=["--use-gl=angle","--use-angle=swiftshader","--enable-webgl"],
    )
    page=browser.new_page(viewport={"width":1450,"height":950})
    page.goto("http://127.0.0.1:8501",wait_until="domcontentloaded",timeout=60000)
    for key,label,title,resource in SECTORS:
        page.get_by_text("1 · Ingreso de datos y modelo matemático").wait_for(timeout=45000)
        combo=page.get_by_role("combobox",name="Escenario operativo")
        combo.click()
        page.get_by_role("option",name=label,exact=True).click()
        page.get_by_role("button",name="Guardar y validar configuración").click()
        page.get_by_text("2 · Vista previa: entorno construido sin movimiento").wait_for(timeout=90000)
        inner=page.frame_locator("iframe").first
        inner.locator("canvas").wait_for(timeout=60000)
        assert title in inner.locator(".brand b").inner_text(),f"Escena equivocada: {key}"
        assert resource in inner.locator("#stat-active").locator("..").inner_text(),f"Terminología errónea: {key}"
        assert inner.locator("canvas").evaluate("(el)=>el.width>0&&el.height>0"),key
        page.screenshot(path=f"visual-artifacts/v3-{key}-preview.png",full_page=True)
        page.get_by_role("button",name="← Volver a ingresar datos").click()
    print("E2E PASS: 4 escenarios 3D correctos con nomenclatura específica, sin Producción")
    browser.close()
