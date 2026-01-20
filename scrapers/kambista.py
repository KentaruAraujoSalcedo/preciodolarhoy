from playwright.async_api import async_playwright

async def scrap_kambista():
    url = "https://kambista.com/"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            # Espera a que aparezcan los elementos correctos
            await page.wait_for_selector("#valcompra", timeout=15000)
            await page.wait_for_selector("#valventa", timeout=15000)

            # Extrae texto
            compra = await page.locator("#valcompra").text_content()
            venta = await page.locator("#valventa").text_content()

            await browser.close()

            return {
                "casa": "Kambista",
                "url": url,
                "compra": float(compra.strip()),
                "venta": float(venta.strip())
            }

    except Exception as e:
        return {
            "casa": "Kambista",
            "url": url,
            "error": f"No se pudo scrapear: {e}"
        }
