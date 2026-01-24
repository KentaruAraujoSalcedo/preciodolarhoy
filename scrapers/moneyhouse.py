# scrapers/moneyhouse.py
import re
from playwright.async_api import async_playwright
from scrapers.utils import normalize_rate

_NUM_RE = re.compile(r"\d+[.,]\d+")

def _extract_number(txt: str):
    if not txt:
        return None
    m = _NUM_RE.search(txt)
    return m.group(0) if m else None

async def scrap_moneyhouse():
    url = "https://moneyhouse.pe/"
    casa = "MoneyHouse"
    browser = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ],
            )

            context = await browser.new_context(
                locale="es-PE",
                timezone_id="America/Lima",
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 720},
            )

            page = await context.new_page()
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")

            # si hay banner de cookies
            try:
                await page.get_by_role("button", name=re.compile("ACEPTAR", re.I)).click(timeout=3000)
            except Exception:
                pass

            compra_wrap = page.locator(".views-field-field-t-c-compra").first
            venta_wrap  = page.locator(".views-field-field-t-c-venta").first

            await compra_wrap.wait_for(state="attached", timeout=40000)
            await venta_wrap.wait_for(state="attached", timeout=40000)

            # Espera hasta que el TEXTO del contenedor tenga un número válido
            await page.wait_for_function(
                """() => {
                    const getNum = (sel) => {
                        const el = document.querySelector(sel);
                        if (!el) return null;
                        const t = (el.textContent || "").trim();
                        const m = t.match(/\\d+[\\.,]\\d+/);
                        return m ? m[0] : null;
                    };

                    const c = getNum(".views-field-field-t-c-compra");
                    const v = getNum(".views-field-field-t-c-venta");
                    if (!c || !v) return false;

                    const cf = parseFloat(c.replace(",", "."));
                    const vf = parseFloat(v.replace(",", "."));
                    return cf > 0 && vf > 0 && c !== "0.000" && v !== "0.000";
                }""",
                timeout=40000
            )

            compra_text = (await compra_wrap.text_content() or "").strip()
            venta_text  = (await venta_wrap.text_content() or "").strip()

            compra_num = _extract_number(compra_text)
            venta_num  = _extract_number(venta_text)

            compra = normalize_rate(compra_num) if compra_num else None
            venta  = normalize_rate(venta_num) if venta_num else None

            return {"casa": casa, "url": url, "compra": compra, "venta": venta}

    except Exception as e:
        return {"casa": casa, "url": url, "compra": None, "venta": None, "error": f"No se pudo scrapear: {e}"}

    finally:
        if browser:
            await browser.close()