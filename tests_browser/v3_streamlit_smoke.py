"""End-to-end browser validation of the actual Streamlit + Three.js v3 workflow."""
from pathlib import Path
from playwright.sync_api import sync_playwright

URL="http://127.0.0.1:8501"

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--use-gl=angle","--use-angle=swiftshader","--enable-webgl"])
    page=browser.new_page(viewport={"width":1460,"height":980},device_scale_factor=1)
    page.goto(URL,wait_until="domcontentloaded",timeout=60000)
    page.get_by_text("Decision Lab 3.0 · Simulador multimodelo").wait_for(timeout=45000)
    assert page.get_by_text("1 · Ingreso de datos y modelo matemático").is_visible()
    assert page.locator("iframe").count()==0,"No se debe mostrar Three.js antes de configurar"
    page.get_by_role("button",name="Guardar y validar configuración").click()
    page.get_by_text("2 · Vista previa: entorno construido sin movimiento").wait_for(timeout=90000)
    iframe=page.locator("iframe").first
    assert iframe.count()==1,"No se montó el banco 3D"
    internal=page.frame_locator("iframe").first
    internal.locator(".bank3d").wait_for(timeout=45000)
    internal.locator("canvas").wait_for(timeout=60000)
    assert "BANCO" in internal.locator(".brand").inner_text()
    assert internal.locator("canvas").evaluate("(el)=>el.width>0&&el.height>0")
    Path("visual-artifacts").mkdir(exist_ok=True)
    page.screenshot(path="visual-artifacts/v3-preview.png",full_page=True)
    page.get_by_role("button",name="▶ Iniciar simulación desde 0 min").click()
    page.get_by_text("3 · Simulación y monitoreo").wait_for(timeout=90000)
    running=page.frame_locator("iframe").first
    running.locator("canvas").wait_for(timeout=60000)
    assert running.locator("#stat-time").count()==1
    assert running.locator("#graph-queue path").count()==1
    page.screenshot(path="visual-artifacts/v3-running.png",full_page=True)
    print("Browser E2E v3 OK: data-first, preview Three.js canvas, 3D run with synchronized charts")
    browser.close()
