from playwright.async_api import async_playwright

async def scrap_traderperufx():
    url = "https://traderperufx.com/"
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
         
            await page.goto(url, timeout=60000)

            # Esperamos a que al menos 2 elementos <b> visibles carguen
            await page.wait_for_selector("b", timeout=15000)
            bolds = await page.locator("b").all_text_contents()
            tasas_raw = [t.strip() for t in bolds if t.strip().replace('.', '', 1).isdigit()]

        
            if len(tasas_raw) < 2:
                raise Exception("No se encontraron tasas suficientes")

            compra = float(tasas_raw[0])
            venta = float(tasas_raw[1])

            await browser.close()

            return {
                "casa": "TraderPeruFX",
                "url": url,
                "compra": compra,
                "venta": venta
            }

    except Exception as e:
        return {
            "casa": "TraderPeruFX",
            "url": url,
            "error": f"No se pudo scrapear: {e}"
        }
