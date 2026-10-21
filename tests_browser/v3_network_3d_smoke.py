"""E2E Chromium: 3D nodes and per-stage KPIs derived from Python engine."""
from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--use-gl=angle","--use-angle=swiftshader","--enable-webgl"])
    page=browser.new_page(viewport={"width":1490,"height":1040})
    page.goto("http://127.0.0.1:8501",wait_until="domcontentloaded",timeout=60000)
    page.get_by_text("Red de colas",exact=True).first.click()
    page.get_by_text("Red de colas multietapa").wait_for(timeout=45000)
    page.get_by_role("button",name="Simular red").click()
    page.get_by_text("2 · Vista previa 3D de la red · Sin movimiento").wait_for(timeout=90000)
    inner=page.frame_locator("iframe").first
    stage=inner.locator("#stage")
    stage.wait_for(timeout=60000)
    assert stage.get_attribute("data-nodes")=="3",stage.get_attribute("data-nodes")
    assert stage.get_attribute("data-source")=="python-network-events"
    assert stage.get_attribute("data-preview")=="true"
    assert inner.locator(".node").count()==3
    assert inner.locator("canvas").evaluate("(el)=>el.width>0 && el.height>0")
    assert not inner.locator("#loading").count()
    Path("visual-artifacts").mkdir(exist_ok=True)
    page.screenshot(path="visual-artifacts/network-3d-preview.png",full_page=True)
    page.get_by_role("button",name="▶ Iniciar simulación 3D de la red").click()
    page.get_by_text("3 · Red de procesos en movimiento").wait_for(timeout=90000)
    live=page.frame_locator("iframe").first
    live.locator("#play").wait_for(timeout=60000)
    assert live.locator("#stage").get_attribute("data-preview")=="false"
    live.locator("#play").click()
    page.wait_for_timeout(1300)
    assert live.locator("#time").inner_text()!="0.0"
    assert live.locator(".node").count()==3
    assert live.locator(".node .q").count()==3
    assert live.locator(".node .rho").count()==3
    page.screenshot(path="visual-artifacts/network-3d-running.png",full_page=True)
    print("PASS: network 3D uses Python stage occupancy, previews, animates, and shows per-stage KPIs")
    browser.close()
