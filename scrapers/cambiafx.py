# scrapers/cambiafx.py
from playwright.async_api import async_playwright
from scrapers.utils import normalize_rate

async def scrap_cambiafx():
    url = "https://cambiafx.pe/"
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            # Espera a que estén visibles los nodos de tasas
            await page.wait_for_selector(".txt_compra", timeout=15000)
            await page.wait_for_selector(".txt_venta",  timeout=15000)

            # Extraer textos (tolerante a None)
            compra_text = (await page.locator(".txt_compra").text_content() or "").strip()
            venta_text  = (await page.locator(".txt_venta").text_content()  or "").strip()

            # Limpiar prefijo "S/" y normalizar (soporta comas, 0 -> None, etc.)
            compra = normalize_rate(compra_text.replace("S/", "").replace("s/", ""))
            venta  = normalize_rate(venta_text.replace("S/", "").replace("s/", ""))

            return {
                "casa": "CambiaFX",
                "url": url,
                "compra": compra,  # None si inválido
                "venta":  venta,   # None si inválido
            }

    except Exception as e:
        return {
            "casa": "CambiaFX",
            "url": url,
            "compra": None,
            "venta": None,
            "error": f"No se pudo scrapear: {e}",
        }
    finally:
        if browser:
            await browser.close()
