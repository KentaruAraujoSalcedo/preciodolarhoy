# run_scrapers.py
import json
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
from scrapers.kambio import scrap_kambio
from scrapers.mercadocambiario import scrap_mercadocambiario
from scrapers.midpointfx import scrap_midpointfx
from scrapers.moneyhouse import scrap_moneyhouse
from scrapers.perudolar import scrap_perudolar
from scrapers.rissanpe import scrap_rissanpe
from scrapers.securex import scrap_securex
from scrapers.traderperufx import scrap_traderperufx
from scrapers.srcambio import scrap_srcambio
from scrapers.intercambialo import scrap_intercambialo
from scrapers.kallpacambios import scrap_kallpacambios
from scrapers.safex import scrap_safex
from scrapers.tucambista import scrap_tucambista
from scrapers.vipcapitalbusiness import scrap_vipcapitalbusiness
from scrapers.x_cambio import scrap_x_cambio
from scrapers.yanki import scrap_yanki
from scrapers.rextie import scrap_rextie
from scrapers.kambista import scrap_kambista
from scrapers.tkambio import scrap_tkambio
from scrapers.inkamoney import scrap_inkamoney
from scrapers.cambioseguro import scrap_cambioseguro
from scrapers.okane import scrap_okane
from scrapers.jetperu import scrap_jetperu
from scrapers.dichikash import scrap_dichikash
from scrapers.instakash import scrap_instakash
from scrapers.megamoney import scrap_megamoney
from scrapers.smartdollar import scrap_smartdollar
from scrapers.cambiox import scrap_cambiox
from scrapers.westernunion import scrap_westernunion
from scrapers.zonadolar import scrap_zonadolar
from scrapers.dolarex import scrap_dolarex
from scrapers.cambix import scrap_cambix
from scrapers.dlsmoney import scrap_dlsmoney
from scrapers.dinersfx import scrap_dinersfx
from scrapers.sunat import scrap_sunat


async def main():
    resultados = [
        await scrap_yanki(),
        await scrap_rextie(),
        await scrap_kambista(),
        await scrap_tkambio(),
        await scrap_inkamoney(),
        await scrap_cambioseguro(),
        await scrap_okane(),
        await scrap_jetperu(),
        await scrap_dichikash(),
        await scrap_instakash(),
        await scrap_megamoney(),
        await scrap_smartdollar(),
        await scrap_cambiox(),
        await scrap_chaskidolar(),
        await scrap_intercambialo(),
        await scrap_westernunion(),
        await scrap_kallpacambios(),
        await scrap_billex(),        
        await scrap_safex(),   
        await scrap_cambiafx(),   
        await scrap_acomo(),   
        await scrap_zonadolar(),  
        await scrap_srcambio(),  
        await scrap_kambio(),  
        await scrap_cambiomundial(),  
        await scrap_traderperufx(),  
        await scrap_perudolar(),  
        await scrap_midpointfx(),  
        await scrap_cambiosol(),  
        await scrap_x_cambio(), 
        await scrap_rissanpe(), 
        await scrap_cambiomas(),
        await scrap_moneyhouse(),
        await scrap_mercadocambiario(),
        await scrap_vipcapitalbusiness(),
        await scrap_inticambio(),
        await scrap_dolarex(),
        await scrap_cambix(),
        await scrap_dlsmoney(),
        await scrap_dinersfx(),
        await scrap_securex(),
        await scrap_chapacambio(),
        await scrap_tucambista(),
        await scrap_hirpower(),
        await scrap_cambiodigitalperu(),
        await scrap_dollarhouse(),
        await scrap_global66(),
        await scrap_sunat(),


   

    ]
    with open("data/tasas.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

       # === GUARDAR HISTÓRICO CON VALORES DE SUNAT ===
    from datetime import date
    import os

    # Buscar el valor que vino del scraper SUNAT
    sunat_data = next((r for r in resultados if r["casa"] == "SUNAT"), None)

    if sunat_data and sunat_data["compra"] and sunat_data["venta"]:
        sunat_compra = sunat_data["compra"]
        sunat_venta = sunat_data["venta"]
        hoy = str(date.today())

        historico_path = "data/historico.json"
        if os.path.exists(historico_path):
            with open(historico_path, "r", encoding="utf-8") as f:
                historico = json.load(f)
        else:
            historico = []

        # Eliminar el registro de hoy si ya existe
        historico = [d for d in historico if d["fecha"] != hoy]

        # Agregar el nuevo registro
        historico.append({
            "fecha": hoy,
            "compra": sunat_compra,
            "venta": sunat_venta
        })

        with open(historico_path, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)

        print(f"📈 Histórico SUNAT actualizado: {hoy} Compra {sunat_compra} / Venta {sunat_venta}")
    else:
        print("⚠️ No se encontró información válida de SUNAT para el histórico.")



    print("✅ Tasas guardadas en data/tasas.json")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())