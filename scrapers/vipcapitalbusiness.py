# scrapers/vipcapitalbusiness.py
from playwright.async_api import async_playwright
import re
from scrapers.utils import normalize_rate

async def scrap_vipcapitalbusiness():
    url = "https://www.vipcapitalbusiness.com/"
    casa = "VipCapital"
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)

            # Esperar que existan los valores
            await page.wait_for_selector("#tc_compra", timeout=15000)
            await page.wait_for_selector("#tc_venta",  timeout=15000)

            compra_raw = await page.locator("#tc_compra").text_content()
            venta_raw  = await page.locator("#tc_venta").text_content()

            # Extraer número tolerando comas/puntos y texto adicional
            def _clean(txt: str) -> str:
                # deja solo dígitos, . y , luego homogeneiza coma -> punto
                return re.sub(r"[^\d.,]", "", (txt or "")).replace(",", ".")

            compra = normalize_rate(_clean(compra_raw))
            venta  = normalize_rate(_clean(venta_raw))

            return {
                "casa": casa,
                "url": url,
                "compra": compra,  # None si 0 / inválido / fuera de rango
                "venta":  venta,   # None si 0 / inválido / fuera de rango
            }

    except Exception as e:
        return {
            "casa": casa,
            "url": url,
            "compra": None,
            "venta": None,
            "error": f"No se pudo scrapear: {e}",
        }
    finally:
        if browser:
            await browser.close()
