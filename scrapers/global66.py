from playwright.async_api import async_playwright
import re

async def scrap_global66():
    url = "https://www.global66.com/pe/envios-de-dinero/"
    casa = "Global66"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)

            # Esperamos que aparezca un texto que contenga "USD ="
            await page.wait_for_function(
                """() => {
                    const elements = Array.from(document.querySelectorAll('p'));
                    return elements.some(p => p.textContent.includes("USD ="));
                }""",
                timeout=20000
            )

            # Extraemos todos los <p> y buscamos el que tiene "USD ="
            paragraphs = await page.locator("p").all_text_contents()

            match_text = next((t for t in paragraphs if "USD = " in t), None)
            if not match_text:
                raise Exception("No se encontró texto tipo 'USD = ...'")

            match = re.search(r"1\s*USD\s*=\s*(\d+\.\d+)", match_text)
            if not match:
                raise Exception("No se encontró el valor numérico")

            valor = float(match.group(1))

            await browser.close()

            return {
                "casa": casa,
                "url": url,
                "compra": valor,
                "venta": valor
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
    resultado = asyncio.run(scrap_global66())
    print(resultado)
