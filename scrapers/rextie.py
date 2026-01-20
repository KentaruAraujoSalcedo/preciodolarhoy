from playwright.async_api import async_playwright

async def scrap_rextie():
    url = "https://www.rextie.com/"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)

            # Esperar a que aparezcan los contenedores
            await page.wait_for_selector(".buy.flex-1", timeout=10000)
            await page.wait_for_selector(".sell.flex-1", timeout=10000)

            # Esperar a que el valor de compra deje de ser 3.0 (valor temporal inicial)
            await page.wait_for_function(
                """() => {
                    const el = document.querySelector('.buy.flex-1');
                    return el && el.innerText.includes('3.') && !el.innerText.includes('3.0');
                }""",
                timeout=10000
            )

            compra_text = await page.locator(".buy.flex-1").text_content()
            venta_text = await page.locator(".sell.flex-1").text_content()

            # Extraer el número decimal del texto
            compra = float([x for x in compra_text.split() if x.replace(".", "").isdigit()][0])
            venta = float([x for x in venta_text.split() if x.replace(".", "").isdigit()][0])

            await browser.close()

            return {
                "casa": "Rextie",
                "url": url,
                "compra": compra,
                "venta": venta
            }

    except Exception as e:
        return {
            "casa": "Rextie",
            "url": url,
            "error": f"No se pudo scrapear: {e}"
        }
