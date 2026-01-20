from playwright.async_api import async_playwright
import asyncio

async def scrap_srcambio():
    url = "https://srcambio.pe/"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)

            # Espera que los valores cambien de 0 a reales
            await page.wait_for_function("""
                () => {
                    const els = Array.from(document.querySelectorAll('.item-text-amount'));
                    return els.length >= 2 && els.every(e => parseFloat(e.textContent.trim()) > 0);
                }
            """, timeout=15000)

            # Extraer nuevamente los valores
            tasas_raw = await page.locator(".item-text-amount").all_text_contents()

            # Limpiar y convertir
            tasas = [float(t.strip()) for t in tasas_raw if t.strip().replace(".", "", 1).isdigit()]
            if len(tasas) < 2:
                raise Exception("No se encontraron suficientes tasas válidas")

            compra, venta = tasas[0], tasas[1]

            await browser.close()
            return {
                "casa": "SRCambio",
                "url": url,
                "compra": compra,
                "venta": venta
            }

    except Exception as e:
        return {
            "casa": "SRCambio",
            "url": url,
            "error": f"No se pudo scrapear: {e}"
        }

# Para pruebas directas
if __name__ == "__main__":
    resultado = asyncio.run(scrap_srcambio())

