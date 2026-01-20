from playwright.async_api import async_playwright
import re

async def scrap_tucambista():
    url = "https://tucambista.pe/"
    casa = "TuCambista"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
          
            await page.goto(url, timeout=60000)

            # Espera que aparezcan los valores de tipo de cambio que contienen "3."
            await page.wait_for_function(
                """() => {
                    const spans = Array.from(document.querySelectorAll('span'));
                    return spans.filter(el => el.textContent.includes("3.")).length >= 2;
                }""",
                timeout=15000
            )

            # Extraemos todos los spans visibles que contengan valores tipo "3.5xx"
            spans = await page.locator("span").all_text_contents()
         

            # Filtrar spans que parecen tasas
            tasas = [s for s in spans if re.fullmatch(r"3\.\d{3}", s.strip())]

            if len(tasas) < 2:
                raise Exception("No se encontraron suficientes tasas válidas")

            compra = float(tasas[0])
            venta = float(tasas[1])

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
    resultado = asyncio.run(scrap_tucambista())
    print(resultado)
