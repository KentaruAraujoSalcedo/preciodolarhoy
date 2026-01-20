from playwright.async_api import async_playwright

async def scrap_inkamoney():
    url = "https://inkamoney.com/"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            # Esperar ambos elementos
            await page.wait_for_selector(".prices .h6 span", timeout=15000)

            spans = page.locator(".prices .h6 span")
            valores = await spans.all_text_contents()

            # Limpiar y convertir a float
            valores = [float(t.replace("S/", "").strip()) for t in valores if "S/" in t]

            compra = valores[0] if len(valores) > 0 else None
            venta = valores[1] if len(valores) > 1 else None

            await browser.close()

            return {
                "casa": "InkaMoney",
                "url": url,
                "compra": compra,
                "venta": venta
            }

    except Exception as e:
        return {
            "casa": "InkaMoney",
            "url": url,
            "error": f"No se pudo scrapear: {e}"
        }
