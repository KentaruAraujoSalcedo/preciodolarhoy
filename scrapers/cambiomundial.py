# scrapers/cambiomundial.py
from playwright.async_api import async_playwright
from scrapers.utils import normalize_rate

async def scrap_cambiomundial():
    url = "https://www.cambiomundial.com/"
    casa = "CambioMundial"
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)
            await page.wait_for_selector("#lblvalorcompra", timeout=15000)
            await page.wait_for_selector("#lblvalorventa",  timeout=15000)

            compra_text = (await page.locator("#lblvalorcompra").inner_text() or "").strip()
            venta_text  = (await page.locator("#lblvalorventa").inner_text()  or "").strip()

            # Normaliza (acepta "3,567", "3.567", etc.; 0/raros -> None)
            compra = normalize_rate(compra_text.replace("S/", "").replace("s/", ""))
            venta  = normalize_rate(venta_text.replace("S/", "").replace("s/", ""))

            return {
                "casa": casa,
                "url": url,
                "compra": compra,   # None si inválido
                "venta":  venta,    # None si inválido
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
