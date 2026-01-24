# scrapers/moneyhouse.py
import re
from playwright.async_api import async_playwright
from scrapers.utils import normalize_rate

async def scrap_moneyhouse():
    url = "https://moneyhouse.pe/"
    casa = "MoneyHouse"
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

            # (Opcional) cerrar cookies si aparece
            try:
                await page.get_by_role("button", name=re.compile("ACEPTAR", re.I)).click(timeout=3000)
            except Exception:
                pass

            compra_sel = ".views-field-field-t-c-compra span.cant"
            venta_sel  = ".views-field-field-t-c-venta  span.cant"

            compra_loc = page.locator(compra_sel).first
            venta_loc  = page.locator(venta_sel).first

            # OJO: en GitHub puede no estar "visible", pero sí existe en el DOM
            await compra_loc.wait_for(state="attached", timeout=40000)
            await venta_loc.wait_for(state="attached", timeout=40000)

            # Espera valores reales (no vacío / no 0 / etc)
            await page.wait_for_function(
                """() => {
                    const pick = (sel) => {
                        const el = document.querySelector(sel);
                        if (!el) return null;
                        const t = (el.textContent || "").trim();
                        const m = t.match(/\\d+[\\.,]\\d+/);
                        return m ? m[0] : null;
                    };

                    const c = pick(".views-field-field-t-c-compra span.cant");
                    const v = pick(".views-field-field-t-c-venta span.cant");

                    if (!c || !v) return false;

                    const cf = parseFloat(c.replace(",", "."));
                    const vf = parseFloat(v.replace(",", "."));

                    return cf > 0 && vf > 0 && c !== "0" && v !== "0" && c !== "0.000" && v !== "0.000";
                }""",
                timeout=40000
            )

            compra_text = (await compra_loc.text_content() or "").strip()
            venta_text  = (await venta_loc.text_content()  or "").strip()

            compra = normalize_rate(compra_text)
            venta  = normalize_rate(venta_text)

            return {"casa": casa, "url": url, "compra": compra, "venta": venta}

    except Exception as e:
        return {"casa": casa, "url": url, "compra": None, "venta": None, "error": f"No se pudo scrapear: {e}"}

    finally:
        if browser:
            await browser.close()