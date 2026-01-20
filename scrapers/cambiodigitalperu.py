# scrapers/cambiodigitalperu.py
from playwright.async_api import async_playwright
import re
from scrapers.utils import normalize_rate

async def scrap_cambiodigitalperu():
    url = "https://cambiodigitalperu.com"
    casa = "CambioDigitalPeru"
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            # Espera a que carguen los elementos de dólar
            await page.wait_for_selector("#dolarcompra", timeout=15000)
            await page.wait_for_selector("#dolarventa",  timeout=15000)

            compra_raw = await page.locator("#dolarcompra").text_content()
            venta_raw  = await page.locator("#dolarventa").text_content()

            # Extrae solo números y punto; tolera None
            compra_txt = re.sub(r"[^\d.,]", "", (compra_raw or "")).replace(",", ".")
            venta_txt  = re.sub(r"[^\d.,]", "", (venta_raw  or "")).replace(",", ".")

            compra = normalize_rate(compra_txt)
            venta  = normalize_rate(venta_txt)

            return {
                "casa": casa,
                "url": url,
                "compra": compra,   # None si 0/ inválido
                "venta":  venta,    # None si 0/ inválido
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

# Test manual (opcional)
# if __name__ == "__main__":
#     import asyncio
#     print(asyncio.run(scrap_cambiodigitalperu()))
