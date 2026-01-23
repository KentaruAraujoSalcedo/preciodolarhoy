# scrapers/cambiafx.py
import re
from playwright.async_api import async_playwright
from scrapers.utils import normalize_rate


def _extract_last_number(text: str):
    """
    Busca números tipo 3.3420 / 3,3420 dentro de cualquier texto
    y devuelve el ÚLTIMO que encuentre (normalmente es el valor final).
    """
    if not text:
        return None

    # captura 3.3420 o 3,3420
    matches = re.findall(r"\d+[.,]\d+", text)
    if not matches:
        return None

    return matches[-1]  # el último suele ser la tasa


async def scrap_cambiafx():
    url = "https://cambiafx.pe/"
    casa = "CambiaFX"
    browser = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000, wait_until="domcontentloaded")

            # (Opcional) cerrar cookies si sale
            try:
                await page.get_by_role("button", name=re.compile("ACEPTAR", re.I)).click(timeout=2000)
            except Exception:
                pass

            # Botones por aria-label (estable)
            buy_btn = page.locator('button[aria-label*="compra de dólares" i]').first
            sell_btn = page.locator('button[aria-label*="venta de dólares" i]').first

            await buy_btn.wait_for(state="visible", timeout=20000)
            await sell_btn.wait_for(state="visible", timeout=20000)

            compra_raw = (await buy_btn.inner_text()).strip()
            venta_raw = (await sell_btn.inner_text()).strip()

            compra_num = _extract_last_number(compra_raw)
            venta_num = _extract_last_number(venta_raw)

            compra = normalize_rate(compra_num) if compra_num else None
            venta = normalize_rate(venta_num) if venta_num else None

            return {
                "casa": casa,
                "url": url,
                "compra": compra,
                "venta": venta,
            }

    except Exception as e:
        return {
            "casa": casa,
            "url": url,
            "compra": None,
            "venta": None,
            "error": f"No se pudo scrapear: {e}",
        }
    finally:
        if browser:
            await browser.close()
