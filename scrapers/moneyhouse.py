from playwright.async_api import async_playwright
import asyncio
import re

async def scrap_moneyhouse():
    url = "https://moneyhouse.pe/"
    casa = "MoneyHouse"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)

            # Extraer todos los spans .cantamt, incluso si están ocultos
            tasas_raw = await page.eval_on_selector_all(
                ".cantant",
                "els => els.map(el => el.textContent.trim())"
            )


            if not tasas_raw or len(tasas_raw) < 2:
                raise ValueError("No se encontraron suficientes tasas")

            compra = float(re.sub(r"[^\d.]", "", tasas_raw[0]))
            venta = float(re.sub(r"[^\d.]", "", tasas_raw[1]))

            if compra == 0.0 or venta == 0.0:
                raise ValueError("Tasas parecen estar en 0.0")

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
    resultado = asyncio.run(scrap_moneyhouse())
    print(resultado)
