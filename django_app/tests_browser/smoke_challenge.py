"""Playwright end-to-end checks for unified app and event-driven illustrations."""
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path("visual-artifacts")
OUT.mkdir(exist_ok=True)
errors = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page(viewport={"width":1440,"height":900},device_scale_factor=1)
    page.on("pageerror",lambda error:errors.append(str(error)))
    page.goto("http://127.0.0.1:8000/aplicativo-app/",wait_until="domcontentloaded")
    page.locator("#challenge-scenario").wait_for(state="visible")
    assert page.locator(".arena-model").count()==8
    assert page.locator(".sector-card").count()==5
    page.locator(".sector-card[data-sector='hospital']").click()
    assert page.locator("#challenge-scenario").input_value()=="hospital"
    assert page.locator(".sector-card[data-sector='hospital']").get_attribute("aria-pressed")=="true"
    assert page.locator("#classic-lab").is_visible()
    assert page.locator("#c-scene-art").evaluate("(img)=>img.complete && img.naturalWidth>0")
    page.screenshot(path=str(OUT/"01-aplicativo-app.png"),full_page=True)
    for key in ("banco","hospital","supermercado","fabrica","logistica"):
        page.locator("#challenge-scenario").select_option(key)
        page.wait_for_function("document.querySelector('#c-scene-art').complete && document.querySelector('#c-scene-art').naturalWidth>0")
        assert page.locator("#c-scene-art").get_attribute("src").endswith(key+".svg")
        page.locator("#scene-shell").screenshot(path=str(OUT/("escena-"+key+".png")))
    page.locator("#challenge-scenario").select_option("banco")
    page.locator("#lab-run").click()
    page.wait_for_function("document.querySelector('#lab-kpis').children.length>=8",timeout=30000)
    page.screenshot(path=str(OUT/"02-laboratorio-modelos.png"),full_page=True)
    page.locator("#hour-0").fill("2")
    page.locator("#hour-1").fill("5")
    page.locator("#challenge-run").click()
    page.wait_for_function("document.querySelector('#challenge-kpis').children.length>=8",timeout=30000)
    assert page.locator("#scene-shell .dynamic-station").count()==2,"Expected exactly 2 physical service desks at t=0"
    for event_index in range(12, min(160, int(page.locator("#challenge-scrub").get_attribute("max"))), 7):
        page.locator("#challenge-scrub").evaluate("(e, value)=>{e.value=String(value);e.dispatchEvent(new Event('input',{bubbles:true}));}", event_index)
        if page.locator(".scene-avatar").count()>0:
            break
    assert page.locator(".scene-avatar").count()>=1,"Dynamic customer avatars never appeared at occupied frames"
    for event_index in range(30, min(350,int(page.locator("#challenge-scrub").get_attribute("max"))),5):
        page.locator("#challenge-scrub").evaluate("(e, value)=>{e.value=String(value);e.dispatchEvent(new Event('input',{bubbles:true}));}",event_index)
        if page.locator("#c-clock").inner_text().startswith("01:"):
            break
    assert page.locator("#scene-shell .dynamic-station").count()==5,"Five configured desks must appear in hour two"
    assert page.locator("#scene-shell .dynamic-station[data-station='5']").count()==1
    page.locator("#challenge-play").click()
    page.wait_for_timeout(550)
    page.locator("#challenge-play").click()
    page.locator("#challenge-intervene-count").fill("5")
    page.locator("#challenge-intervene").click()
    page.wait_for_function("document.querySelector('#challenge-actions').textContent.includes('Intervenciones:')",timeout=30000)
    page.screenshot(path=str(OUT/"03-mision-intervencion.png"),full_page=True)
    page.goto("http://127.0.0.1:8000/simular/colas/",wait_until="domcontentloaded")
    page.wait_for_function("document.querySelector('#legacy-dynamic-scene .dynamic-station')!==null",timeout=30000)
    assert page.locator("#legacy-dynamic-scene .dynamic-station").count()==2
    assert page.locator("#legacy-dynamic-scene .sim-legacy-bg").evaluate("(img)=>img.complete && img.naturalWidth>0")
    page.locator("#sim-servers").fill("5")
    page.locator("#simulator-form").locator("button[type=submit]").click()
    page.wait_for_function("document.querySelectorAll('#legacy-dynamic-scene .dynamic-station').length === 5",timeout=30000)
    page.locator("#legacy-dynamic-scene").screenshot(path=str(OUT/"simulador-clasico-dinamico-5-puestos.png"))
    phone=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=1)
    phone.on("pageerror",lambda error:errors.append(str(error)))
    phone.goto("http://127.0.0.1:8000/aplicativo-app/",wait_until="domcontentloaded")
    phone.locator("#challenge-scenario").wait_for(state="visible")
    phone.screenshot(path=str(OUT/"04-aplicativo-movil.png"),full_page=True)
    assert phone.evaluate("document.documentElement.scrollWidth <= innerWidth + 2"),"Horizontal mobile overflow"
    browser.close()
assert not errors,"Browser errors: "+repr(errors)
print("E2E OK: unified app, 5 sector scenes, 2-to-5 changing desks, legacy 5-counter simulator, intervention and mobile")
