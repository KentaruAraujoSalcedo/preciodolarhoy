# scrapers/acomo.py
from playwright.async_api import async_playwright
from scrapers.utils import normalize_rate

async def scrap_acomo():
    url = "https://acomo.com.pe/"
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            # Esperar a que aparezcan los nodos con las tasas
            await page.wait_for_selector("#current_bid", timeout=15000)
            await page.wait_for_selector("#current_offer", timeout=15000)

            # Extraer texto crudo
            compra_text = (await page.locator("#current_bid").text_content() or "").strip()
            venta_text  = (await page.locator("#current_offer").text_content() or "").strip()

            # Limpiar y normalizar (acepta "S/ 3.567", "3,567", etc.)
            compra = normalize_rate(compra_text.replace("S/", "").replace("s/", ""))
            venta  = normalize_rate(venta_text.replace("S/", "").replace("s/", ""))

            return {
                "casa": "Acomo",
                "url": url,
                "compra": compra,  # None si es 0/ inválido
                "venta":  venta,   # None si es 0/ inválido
            }

    except Exception as e:
        return {
            "casa": "Acomo",
            "url": url,
            "compra": None,
            "venta": None,
            "error": f"No se pudo scrapear: {e}",
        }
    finally:
        if browser:
            await browser.close()
