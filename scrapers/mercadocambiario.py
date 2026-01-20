# scrapers/mercadocambiario.py
from playwright.async_api import async_playwright
import re
from scrapers.utils import normalize_rate

async def scrap_mercadocambiario():
    url = "https://mercadocambiario.pe/"
    casa = "MercadoCambiario"
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)

            # Espera a que aparezcan los spans con montos
            await page.wait_for_selector("div.buy span.amount",  timeout=15000)
            await page.wait_for_selector("div.sell span.amount", timeout=15000)

            # Extraer texto crudo (tolerante a None)
            compra_raw = await page.locator("div.buy span.amount").text_content()
            venta_raw  = await page.locator("div.sell span.amount").text_content()

            # Limpiar a "3.567" (soporta comas, S/, espacios)
            compra_txt = re.sub(r"[^\d.,]", "", (compra_raw or "")).replace(",", ".")
            venta_txt  = re.sub(r"[^\d.,]", "", (venta_raw  or "")).replace(",", ".")

            compra = normalize_rate(compra_txt)  # -> None si 0/ inválido/fuera de rango
            venta  = normalize_rate(venta_txt)

            return {
                "casa": casa,
                "url": url,
                "compra": compra,
                "venta":  venta,
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
