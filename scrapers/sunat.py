from playwright.async_api import async_playwright
from datetime import date
import re

async def scrap_sunat():
    url = "https://www.sunat.gob.pe/cl-at-ittipcam/tcS01Alias"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_selector("div.event", timeout=30000)

            # Fecha de hoy (SUNAT usa data-date con un ISO + hora Z)
            hoy = date.today().isoformat()
            selector = f'td[data-date="{hoy}T05:00:00.000Z"]'

            celda = await page.query_selector(selector)
            if not celda:
                raise Exception(f"No se encontró el día actual en el calendario. selector={selector}")

            textos = await celda.inner_text()

            compra = re.search(r"Compra\s+\"?\s*([\d.]+)", textos)
            venta  = re.search(r"Venta\s+\"?\s*([\d.]+)", textos)

            if not (compra and venta):
                raise Exception(f"No se encontró texto de compra/venta. Textos: {textos!r}")

            return {
                "casa": "SUNAT",
                "url": url,
                "compra": float(compra.group(1)),
                "venta": float(venta.group(1)),
            }

    except Exception as e:
        # IMPORTANTE: nunca devolver None, siempre devolver dict para que aparezca en el JSON
        return {
            "casa": "SUNAT",
            "url": url,
            "compra": None,
            "venta": None,
            "error": str(e),
        }
