# scrapers/traderperufx.py
from playwright.async_api import async_playwright
from scrapers.utils import normalize_rate

async def scrap_traderperufx():
    url = "https://traderperufx.com/"
    casa = "TraderPeruFX"
    browser = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Carga inicial
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")

            # Espera a que existan los nodos
            await page.wait_for_selector("#display-compra", timeout=25000)
            await page.wait_for_selector("#display-venta", timeout=25000)

            # Espera a que NO estén vacíos y NO sean 0/0.000
            await page.wait_for_function(
                """
                () => {
                  const c = document.querySelector("#display-compra");
                  const v = document.querySelector("#display-venta");
                  if (!c || !v) return false;

                  const ct = (c.textContent || "").trim();
                  const vt = (v.textContent || "").trim();

                  const toNum = (s) => {
                    const m = s.replace(",", ".").match(/\\d+(\\.\\d+)?/);
                    return m ? parseFloat(m[0]) : 0;
                  };

                  const cn = toNum(ct);
                  const vn = toNum(vt);

                  return cn > 0 && vn > 0;
                }
                """,
                timeout=25000
            )

            compra_text = (await page.locator("#display-compra").text_content() or "").strip()
            venta_text  = (await page.locator("#display-venta").text_content() or "").strip()

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
