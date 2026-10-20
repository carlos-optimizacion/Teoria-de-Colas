"""Headless smoke test and screenshots of Decision Lab Challenge.
Run after starting Django on http://127.0.0.1:8000.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path("visual-artifacts")
OUT.mkdir(exist_ok=True)
errors = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    desktop = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    desktop.on("pageerror", lambda error: errors.append(str(error)))
    desktop.goto("http://127.0.0.1:8000/challenge/", wait_until="domcontentloaded")
    desktop.locator("#challenge-scenario").wait_for(state="visible")
    assert desktop.locator(".arena-model").count() == 8, "Existing models missing"
    assert desktop.locator("#classic-lab").is_visible(), "Classic lab missing"
    desktop.screenshot(path=str(OUT / "01-arena-desktop.png"), full_page=True)
    desktop.locator("#lab-run").click()
    desktop.wait_for_function(
        "document.querySelector('#lab-kpis').children.length >= 8", timeout=30000)
    assert "Mini-reto" in desktop.locator("#lab-result").inner_text() or "Sistema" in desktop.locator("#lab-result").inner_text()
    desktop.screenshot(path=str(OUT / "02-classic-model.png"), full_page=True)
    desktop.locator("#challenge-run").click()
    desktop.wait_for_function(
        "document.querySelector('#challenge-kpis').children.length >= 8", timeout=30000)
    desktop.locator("#challenge-play").click()
    desktop.wait_for_timeout(600)
    desktop.locator("#challenge-play").click()
    desktop.locator("#challenge-intervene-count").fill("5")
    desktop.locator("#challenge-intervene").click()
    desktop.wait_for_function(
        "document.querySelector('#challenge-actions').textContent.includes('Intervenciones:')",
        timeout=30000)
    desktop.screenshot(path=str(OUT / "03-mission-intervention.png"), full_page=True)
    mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    mobile.on("pageerror", lambda error: errors.append(str(error)))
    mobile.goto("http://127.0.0.1:8000/challenge/", wait_until="domcontentloaded")
    mobile.locator("#challenge-scenario").wait_for(state="visible")
    mobile.screenshot(path=str(OUT / "04-arena-mobile.png"), full_page=True)
    # Allow for 1px pixel rounding, but no horizontal scrolling.
    assert mobile.evaluate("document.documentElement.scrollWidth <= innerWidth + 2"), "Mobile horizontal overflow"
    browser.close()
assert not errors, "Browser JavaScript errors: " + repr(errors)
print("Browser smoke passed: legacy model + management game + intervention + responsive layout")
