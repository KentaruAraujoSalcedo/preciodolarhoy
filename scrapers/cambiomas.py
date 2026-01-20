# scrapers/cambiomas.py
from playwright.async_api import async_playwright
import re
from scrapers.utils import normalize_rate

async def scrap_cambiomas():
    url = "https://cambiomas.com.pe/"
    casa = "CambioMas"
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            # Espera a que existan los nodos con precios
            await page.wait_for_selector("#pCompra", timeout=15000)
            await page.wait_for_selector("#pVenta",  timeout=15000)

            # Extrae textos crudos (tolerante a None)
            compra_raw = await page.locator("#pCompra").text_content()
            venta_raw  = await page.locator("#pVenta").text_content()

            # Limpia y normaliza (soporta "S/ 3,567", "3.567", etc.)
            compra_txt = re.sub(r"[^\d.,]", "", (compra_raw or "")).replace(",", ".")
            venta_txt  = re.sub(r"[^\d.,]", "", (venta_raw  or "")).replace(",", ".")

            compra = normalize_rate(compra_txt)  # -> None si 0 / inválido
            venta  = normalize_rate(venta_txt)   # -> None si 0 / inválido

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

# Test manual (opcional)
# if __name__ == "__main__":
#     import asyncio
#     print(asyncio.run(scrap_cambiomas()))
