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
    Intentos:
      1) IDs (#lblvalorcompra / #lblvalorventa)
      2) Fallback leyendo texto cercano a Compra/Venta
      3) Fallback final por regex al HTML
    """

    # 1) IDs clásicos
    compra_loc = ctx.locator("#lblvalorcompra").first
    venta_loc  = ctx.locator("#lblvalorventa").first

    if await compra_loc.count() and await venta_loc.count():
        # En GH a veces no están "visibles", pero sí en el DOM
        await compra_loc.wait_for(state="attached", timeout=40000)
        await venta_loc.wait_for(state="attached", timeout=40000)

        # Esperar a que se llenen con números > 0
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
            timeout=40000
        )

        compra_txt = (await compra_loc.text_content() or "").strip()
        venta_txt  = (await venta_loc.text_content()  or "").strip()
        return compra_txt, venta_txt

    # 2) Fallback por texto Compra / Venta (sin strict)
    try:
        compra_block = ctx.get_by_text(re.compile(r"\bcompra\b", re.I)).first
        venta_block  = ctx.get_by_text(re.compile(r"\bventa\b", re.I)).first

        if await compra_block.count() and await venta_block.count():
            compra_txt = (await compra_block.locator("xpath=ancestor-or-self::*[1]").text_content() or "").strip()
            venta_txt  = (await venta_block.locator("xpath=ancestor-or-self::*[1]").text_content()  or "").strip()

            if not _extract_number(compra_txt):
                compra_txt = (await compra_block.locator("xpath=ancestor::*[2]").text_content() or "").strip()
            if not _extract_number(venta_txt):
                venta_txt = (await venta_block.locator("xpath=ancestor::*[2]").text_content() or "").strip()

            if _extract_number(compra_txt) and _extract_number(venta_txt):
                return compra_txt, venta_txt
    except Exception:
        pass

    # 3) Fallback por HTML completo (último recurso)
    try:
        html = await ctx.content()
        # intenta sacar 2 números razonables del HTML (primeros dos que parezcan tasas)
        nums = re.findall(r"\b\d[.,]\d{3,4}\b", html)
        if len(nums) >= 2:
            return nums[0], nums[1]
    except Exception:
        pass

    return None, None


async def scrap_cambiomundial():
    url = "https://www.cambiomundial.com/"
    casa = "CambioMundial"
    browser = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )

            context = await browser.new_context(
                locale="es-PE",
                timezone_id="America/Lima",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 720},
            )

            page = await context.new_page()
            await page.goto(url, timeout=60000, wait_until="networkidle")

            # (Opcional) aceptar cookies si aparece
            try:
                await page.get_by_role("button", name=re.compile("ACEPTAR|ACEPTO|OK", re.I)).click(timeout=3000)
            except Exception:
                pass

            # 1) probar en page
            compra_text, venta_text = await _try_extract_from_context(page)

            # 2) probar en iframes si no salió
            if not compra_text or not venta_text:
                for frame in page.frames:
                    c, v = await _try_extract_from_context(frame)
                    if c and v:
                        compra_text, venta_text = c, v
                        break

            compra_num = _extract_number(compra_text or "")
            venta_num  = _extract_number(venta_text  or "")

            compra = normalize_rate(compra_num) if compra_num else None
            venta  = normalize_rate(venta_num)  if venta_num  else None

            if compra is None or venta is None:
                # Esto ayuda muchísimo para debug en GH Actions (se ve en logs)
                snippet = (await page.content())[:1500]
                raise Exception(f"No se pudieron leer tasas (compra={compra_num}, venta={venta_num}). HTML snippet: {snippet}")

            return {"casa": casa, "url": url, "compra": compra, "venta": venta}

    except Exception as e:
        return {"casa": casa, "url": url, "compra": None, "venta": None, "error": f"No se pudo scrapear: {e}"}

    finally:
        if browser:
            await browser.close()