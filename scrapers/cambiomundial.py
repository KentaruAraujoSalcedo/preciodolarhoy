# scrapers/cambiomundial.py
import re
from playwright.async_api import async_playwright
from scrapers.utils import normalize_rate

def _extract_number(txt: str):
    if not txt:
        return None
    m = re.search(r"\d+[.,]\d+", txt)
    return m.group(0) if m else None

async def _try_extract_from_context(ctx):
    """
    ctx puede ser page o frame.
    Intenta extraer compra/venta usando:
    - IDs antiguos
    - Fallback por texto (Compra / Venta) si cambiaron
    """
    # 1) IDs antiguos
    compra_loc = ctx.locator("#lblvalorcompra")
    venta_loc  = ctx.locator("#lblvalorventa")

    if await compra_loc.count() and await venta_loc.count():
        # Espera a que tengan contenido numérico
        await ctx.wait_for_function(
            """() => {
                const c = document.querySelector('#lblvalorcompra')?.textContent || '';
                const v = document.querySelector('#lblvalorventa')?.textContent || '';
                const cm = c.match(/\\d+[\\.,]\\d+/);
                const vm = v.match(/\\d+[\\.,]\\d+/);
                if (!cm || !vm) return false;
                const cf = parseFloat(cm[0].replace(',', '.'));
                const vf = parseFloat(vm[0].replace(',', '.'));
                return cf > 0 && vf > 0;
            }""",
            timeout=25000
        )

        compra_txt = (await compra_loc.text_content() or "").strip()
        venta_txt  = (await venta_loc.text_content() or "").strip()
        return compra_txt, venta_txt

    # 2) Fallback: buscar por texto "Compra" y "Venta" (por si cambiaron IDs)
    # OJO: esto depende del HTML, pero suele funcionar cuando no hay IDs.
    compra_block = ctx.get_by_text(re.compile(r"\bcompra\b", re.I)).first
    venta_block  = ctx.get_by_text(re.compile(r"\bventa\b", re.I)).first

    if await compra_block.count() and await venta_block.count():
        # intenta sacar números desde el contenedor cercano
        compra_txt = (await compra_block.locator("xpath=ancestor-or-self::*[1]").text_content() or "").strip()
        venta_txt  = (await venta_block.locator("xpath=ancestor-or-self::*[1]").text_content() or "").strip()

        # si no encuentra número ahí, sube un nivel más (a veces el número está en el padre)
        if not _extract_number(compra_txt):
            compra_txt = (await compra_block.locator("xpath=ancestor::*[2]").text_content() or "").strip()
        if not _extract_number(venta_txt):
            venta_txt = (await venta_block.locator("xpath=ancestor::*[2]").text_content() or "").strip()

        # valida que haya número
        if _extract_number(compra_txt) and _extract_number(venta_txt):
            return compra_txt, venta_txt

    return None, None


async def scrap_cambiomundial():
    url = "https://www.cambiomundial.com/"
    casa = "CambioMundial"
    browser = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)  # mini respiro

            # 1) intentar en el page directo
            compra_text, venta_text = await _try_extract_from_context(page)

            # 2) si no, probar en iframes
            if not compra_text or not venta_text:
                for frame in page.frames:
                    c, v = await _try_extract_from_context(frame)
                    if c and v:
                        compra_text, venta_text = c, v
                        break

            compra_num = _extract_number(compra_text or "")
            venta_num  = _extract_number(venta_text or "")

            compra = normalize_rate(compra_num) if compra_num else None
            venta  = normalize_rate(venta_num) if venta_num else None

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
