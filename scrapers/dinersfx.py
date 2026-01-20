from playwright.async_api import async_playwright
import re

async def scrap_dinersfx():
    url = "https://dinersfx.pe/"
    casa = "DinersFX"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)

            # Espera hasta que aparezca un span que contenga 3.5xxx
            await page.wait_for_function(
                """() => {
                    const spans = Array.from(document.querySelectorAll("span.font-gotham-book"));
                    return spans.some(span => span.textContent.includes("3.5"));
                }""",
                timeout=15000
            )

            # Extrae todos los spans con clase 'font-gotham-book'
            spans = await page.locator("span.font-gotham-book").all_text_contents()

            # Filtra tasas con expresión regular robusta
            tasas = [float(re.search(r"3\.\d{3,4}", s).group()) for s in spans if re.search(r"3\.\d{3,4}", s)]

            if len(tasas) < 2:
                raise Exception("No se encontraron suficientes tasas válidas")

            compra = tasas[0]
            venta = tasas[1]

            await browser.close()

            return {
                "casa": casa,
                "url": url,
                "compra": compra,
                "venta": venta
            }

    except Exception as e:
        return {
            "casa": casa,
            "url": url,
            "error": f"No se pudo scrapear: {e}"
        }

# Test manual
if __name__ == "__main__":
    import asyncio
    resultado = asyncio.run(scrap_dinersfx())
    print(resultado)
