# run_scrapers.py
import asyncio
import json
import os
from datetime import date

from scrapers.acomo import scrap_acomo
from scrapers.billex import scrap_billex
from scrapers.cambiodigitalperu import scrap_cambiodigitalperu
from scrapers.cambiomas import scrap_cambiomas
from scrapers.cambiomundial import scrap_cambiomundial
from scrapers.cambiosol import scrap_cambiosol
from scrapers.chapacambio import scrap_chapacambio
from scrapers.chaskidolar import scrap_chaskidolar
from scrapers.cambiafx import scrap_cambiafx
from scrapers.dollarhouse import scrap_dollarhouse
from scrapers.global66 import scrap_global66
from scrapers.hirpower import scrap_hirpower
from scrapers.inticambio import scrap_inticambio
from scrapers.kallpacambios import scrap_kallpacambios
from scrapers.kambio import scrap_kambio
from scrapers.kambista import scrap_kambista
from scrapers.megamoney import scrap_megamoney
from scrapers.mercadocambiario import scrap_mercadocambiario
from scrapers.midpointfx import scrap_midpointfx
from scrapers.moneyhouse import scrap_moneyhouse
from scrapers.okane import scrap_okane
from scrapers.perudolar import scrap_perudolar
from scrapers.rextie import scrap_rextie
from scrapers.rissanpe import scrap_rissanpe
from scrapers.safex import scrap_safex
from scrapers.srcambio import scrap_srcambio
from scrapers.securex import scrap_securex
from scrapers.smartdollar import scrap_smartdollar
from scrapers.sunat import scrap_sunat
from scrapers.tkambio import scrap_tkambio
from scrapers.traderperufx import scrap_traderperufx
from scrapers.tucambista import scrap_tucambista
from scrapers.vipcapitalbusiness import scrap_vipcapitalbusiness
from scrapers.westernunion import scrap_westernunion
from scrapers.x_cambio import scrap_x_cambio
from scrapers.yanki import scrap_yanki
from scrapers.zonadolar import scrap_zonadolar
from scrapers.cambiox import scrap_cambiox
from scrapers.cambix import scrap_cambix
from scrapers.dlsmoney import scrap_dlsmoney
from scrapers.dinersfx import scrap_dinersfx
from scrapers.dolarex import scrap_dolarex
from scrapers.inkamoney import scrap_inkamoney
from scrapers.cambioseguro import scrap_cambioseguro
from scrapers.jetperu import scrap_jetperu
from scrapers.dichikash import scrap_dichikash
from scrapers.instakash import scrap_instakash
from scrapers.intercambialo import scrap_intercambialo


async def _safe_call(name: str, coro):
    """Ejecuta un scraper y evita que una excepción tumbe todo el proceso."""
    try:
        res = await coro
        if res is None:
            print(f"⚠️ {name}: devolvió None")
        return res
    except Exception as e:
        print(f"❌ {name}: error -> {e}")
        return None


async def main():
    # Lista de (nombre, coroutine) para log claro
    tasks = [
        ("yanki", scrap_yanki()),
        ("rextie", scrap_rextie()),
        ("kambista", scrap_kambista()),
        ("tkambio", scrap_tkambio()),
        ("inkamoney", scrap_inkamoney()),
        ("cambioseguro", scrap_cambioseguro()),
        ("okane", scrap_okane()),
        ("jetperu", scrap_jetperu()),
        ("dichikash", scrap_dichikash()),
        ("instakash", scrap_instakash()),
        ("megamoney", scrap_megamoney()),
        ("smartdollar", scrap_smartdollar()),
        ("cambiox", scrap_cambiox()),
        ("chaskidolar", scrap_chaskidolar()),
        ("intercambialo", scrap_intercambialo()),
        ("westernunion", scrap_westernunion()),
        ("kallpacambios", scrap_kallpacambios()),
        ("billex", scrap_billex()),
        ("safex", scrap_safex()),
        ("cambiafx", scrap_cambiafx()),
        ("acomo", scrap_acomo()),
        ("zonadolar", scrap_zonadolar()),
        ("srcambio", scrap_srcambio()),
        ("kambio", scrap_kambio()),
        ("cambiomundial", scrap_cambiomundial()),
        ("traderperufx", scrap_traderperufx()),
        ("perudolar", scrap_perudolar()),
        ("midpointfx", scrap_midpointfx()),
        ("cambiosol", scrap_cambiosol()),
        ("x_cambio", scrap_x_cambio()),
        ("rissanpe", scrap_rissanpe()),
        ("cambiomas", scrap_cambiomas()),
        ("moneyhouse", scrap_moneyhouse()),
        ("mercadocambiario", scrap_mercadocambiario()),
        ("vipcapitalbusiness", scrap_vipcapitalbusiness()),
        ("inticambio", scrap_inticambio()),
        ("dolarex", scrap_dolarex()),
        ("cambix", scrap_cambix()),
        ("dlsmoney", scrap_dlsmoney()),
        ("dinersfx", scrap_dinersfx()),
        ("securex", scrap_securex()),
        ("chapacambio", scrap_chapacambio()),
        ("tucambista", scrap_tucambista()),
        ("hirpower", scrap_hirpower()),
        ("cambiodigitalperu", scrap_cambiodigitalperu()),
        ("dollarhouse", scrap_dollarhouse()),
        ("global66", scrap_global66()),
        ("sunat", scrap_sunat()),
    ]

    # Ejecutar secuencialmente (más estable para evitar bloqueos).
    resultados = []
    for name, coro in tasks:
        resultados.append(await _safe_call(name, coro))

    # Quitar Nones y cualquier cosa rara
    resultados = [r for r in resultados if isinstance(r, dict)]

    # Guardar tasas
    os.makedirs("data", exist_ok=True)
    with open("data/tasas.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print("✅ Tasas guardadas en data/tasas.json")

    # === HISTÓRICO SUNAT ===
    sunat_data = next((r for r in resultados if r.get("casa") == "SUNAT"), None)
    if sunat_data and sunat_data.get("compra") and sunat_data.get("venta"):
        sunat_compra = sunat_data["compra"]
        sunat_venta = sunat_data["venta"]
        hoy = str(date.today())

        historico_path = "data/historico.json"
        if os.path.exists(historico_path):
            with open(historico_path, "r", encoding="utf-8") as f:
                historico = json.load(f)
                if not isinstance(historico, list):
                    historico = []
        else:
            historico = []

        historico = [d for d in historico if isinstance(d, dict) and d.get("fecha") != hoy]
        historico.append({"fecha": hoy, "compra": sunat_compra, "venta": sunat_venta})

        with open(historico_path, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)

        print(f"📈 Histórico SUNAT actualizado: {hoy} Compra {sunat_compra} / Venta {sunat_venta}")
    else:
        print("⚠️ SUNAT no devolvió datos válidos. Se deja histórico sin cambios.")


if __name__ == "__main__":
    asyncio.run(main())
