from playwright.async_api import async_playwright
import re

async def scrap_kambio():
    url = "https://www.kambio.online/"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(3000)  # espera carga completa

            # Extrae el texto del div con las tasas visibles
            texto = await page.locator("div.precioMoneda").nth(0).inner_text()

            # Extraer números flotantes del texto
            tasas = re.findall(r"3\.\d{3}", texto)

            if len(tasas) >= 2:
                compra = float(tasas[0])
                venta = float(tasas[1])
            else:
                raise Exception("No se encontraron tasas suficientes")

            await browser.close()

            return {
                "casa": "Kambio",
                "url": url,
                "compra": compra,
                "venta": venta
            }

    except Exception as e:
        return {
            "casa": "Kambio",
            "url": url,
            "error": f"No se pudo scrapear: {e}"
        }
