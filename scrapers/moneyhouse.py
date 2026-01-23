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
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000, wait_until="domcontentloaded")

            # (Opcional) cerrar cookies si aparece
            try:
                await page.get_by_role("button", name=re.compile("ACEPTAR", re.I)).click(timeout=2000)
            except Exception:
                pass

            compra_loc = page.locator(".views-field-field-t-c-compra span.cant").first
            venta_loc  = page.locator(".views-field-field-t-c-venta  span.cant").first

            # Espera a que existan
            await compra_loc.wait_for(state="visible", timeout=25000)
            await venta_loc.wait_for(state="visible", timeout=25000)

            # Espera a que tengan números válidos (no vacío / no 0 / no 0.000)
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
                timeout=25000
            )

            compra_text = (await compra_loc.text_content() or "").strip()
            venta_text  = (await venta_loc.text_content()  or "").strip()

            compra = normalize_rate(compra_text)
            venta  = normalize_rate(venta_text)

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
            "compra": None,
            "venta": None,
            "error": f"No se pudo scrapear: {e}"
        }
    finally:
        if browser:
            await browser.close()
