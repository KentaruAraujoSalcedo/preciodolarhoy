# scrapers/kallpacambios.py
from playwright.async_api import async_playwright
import re
from scrapers.utils import normalize_rate

async def scrap_kallpacambios():
    url = "https://kallpacambios.com/"
    casa = "KallpaCambios"
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            # Espera a que aparezca algún bloque con las tasas
            await page.wait_for_selector(".text-white.text-xs", timeout=15000)
            elementos = await page.locator(".text-white.text-xs").all_text_contents()

            # Extraer valores "S/ 3.56" con regex
            valores = []
            for el in elementos:
                m = re.search(r"S/\s*([\d.,]+)", el)
                if m:
                    valores.append(m.group(1).replace(",", "."))

            # Mapear a compra/venta (si no hay, quedan None)
            compra = normalize_rate(valores[0]) if len(valores) > 0 else None
            venta  = normalize_rate(valores[1]) if len(valores) > 1 else None

            return {
                "casa": casa,
                "url": url,
                "compra": compra,  # None si 0/ inválido
                "venta":  venta,   # None si 0/ inválido
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
