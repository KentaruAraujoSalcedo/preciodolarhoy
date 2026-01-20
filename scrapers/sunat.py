from playwright.async_api import async_playwright
from datetime import date
import re

async def scrap_sunat():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Mostrar navegador
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            url = "https://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias"
            await page.goto(url, timeout=60000)
            await page.wait_for_selector("div.event", timeout=15000)

            # Obtener la fecha de hoy en formato YYYY-MM-DD
            hoy = date.today().isoformat()
            selector = f'td[data-date="{hoy}T05:00:00.000Z"]'

            celda = await page.query_selector(selector)
            if not celda:
                raise Exception("No se encontró el día actual en el calendario")

            textos = await celda.inner_text()
            compra = re.search(r"Compra\s+\"?\s*([\d.]+)", textos)
            venta = re.search(r"Venta\s+\"?\s*([\d.]+)", textos)

            if compra and venta:
                return {
                    "casa": "SUNAT",
                    "url": url,
                    "compra": float(compra.group(1)),
                    "venta": float(venta.group(1))
                }
            else:
                raise Exception("No se encontró texto de compra o venta")

    except Exception as e:
        print(f"❌ Error al scrapear SUNAT: {e}")
        return None
