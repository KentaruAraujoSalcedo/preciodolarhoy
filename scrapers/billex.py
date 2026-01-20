# scrapers/billex.py
from playwright.async_api import async_playwright
from scrapers.utils import normalize_rate

async def scrap_billex():
    url = "https://www.billex.pe/"
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            # OJO: en Billex los ids están invertidos en naming común:
            # #value-buy  = precio al que te compran USD (=> "compra")
            # #value-sell = precio al que te venden USD (=> "venta")

            await page.wait_for_selector("#value-buy", timeout=15000)   # compra
            await page.wait_for_selector("#value-sell", timeout=15000)  # venta

            compra_text = (await page.locator("#value-buy").text_content() or "").strip()
            venta_text  = (await page.locator("#value-sell").text_content() or "").strip()

            # Normaliza (acepta "3,567", "3.567", con/ sin espacios)
            compra = normalize_rate(compra_text)
            venta  = normalize_rate(venta_text)

            return {
                "casa": "Billex",
                "url": url,
                "compra": compra,   # None si es 0/ inválido
                "venta":  venta,    # None si es 0/ inválido
            }

    except Exception as e:
        return {
            "casa": "Billex",
            "url": url,
            "compra": None,
            "venta": None,
            "error": f"No se pudo scrapear: {e}",
        }
    finally:
        if browser:
            await browser.close()
