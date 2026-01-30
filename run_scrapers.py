# run_scrapers.py
import asyncio
import json
import os
from pathlib import Path
from datetime import date, datetime, timezone



# ===== IMPORTS DE SCRAPERS =====
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

# 1) Helper: correr scrapers sin que uno tumbe todo el proceso
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
    
# 2) Backup: cargar backup_tasas.json (manual)
#    Este file debe estar en: data/backup_tasas.json
def load_backup_map(path="data/backup_tasas.json"):
    """
    Lee el backup manual y lo convierte en un mapa:
    backup_map["Rextie"] = {...datos...}
    Retorna (backup_map, fecha_backup).
    """
    p = Path(path)
    if not p.exists():
        return {}, None

    data = json.loads(p.read_text(encoding="utf-8"))
    fecha_backup = data.get("fecha_backup")
    casas = data.get("casas", [])

    # Mapa por nombre exacto de "casa"
    backup_map = {
        c.get("casa"): c
        for c in casas
        if isinstance(c, dict) and c.get("casa")
    }
    return backup_map, fecha_backup


def is_valid_rate(item: dict) -> bool:
    """True si el scraper devolvió compra y venta (no None)."""
    try:
        return item.get("compra") is not None and item.get("venta") is not None
    except Exception:
        return False

def apply_fallbacks(results, last_map, backup_map, fecha_backup=None):
    """
    Mezcla resultados con:
      - scraper válido
      - last known (auto)
      - backup manual
      - missing
    1 SOLO item por casa.
    """
    merged_by_casa = {}

    for r in results:
        if not isinstance(r, dict):
            continue

        casa = r.get("casa")
        if not casa:
            continue

        b = backup_map.get(casa)
        lk = last_map.get(casa) if isinstance(last_map, dict) else None

        # 1) Scraper válido
        if is_valid_rate(r):
            r["source"] = "scraper"
            merged_by_casa[casa] = r
            continue

        # 2) Last known válido
        if isinstance(lk, dict) and lk.get("compra") is not None and lk.get("venta") is not None:
            merged_item = {
                "casa": casa,
                "url": r.get("url") or lk.get("url") or (b.get("url") if isinstance(b, dict) else None),
                "compra": lk.get("compra"),
                "venta": lk.get("venta"),
                "source": "last_known",
                "last_seen": lk.get("last_seen"),
                "backup_fecha": fecha_backup
            }
            if r.get("error"):
                merged_item["scraper_error"] = r["error"]
            merged_by_casa[casa] = merged_item
            continue

        # 3) Backup manual válido
        if isinstance(b, dict) and b.get("compra") is not None and b.get("venta") is not None:
            merged_item = {
                "casa": casa,
                "url": r.get("url") or b.get("url"),
                "compra": b.get("compra"),
                "venta": b.get("venta"),
                "source": "backup",
                "backup_fecha": fecha_backup,
            }
            if r.get("error"):
                merged_item["scraper_error"] = r["error"]
            merged_by_casa[casa] = merged_item
            continue

        # 4) Missing
        merged_item = {
            "casa": casa,
            "url": r.get("url") or (lk.get("url") if isinstance(lk, dict) else None) or (b.get("url") if isinstance(b, dict) else None),
            "source": "missing",
            "backup_fecha": fecha_backup,
        }
        if r.get("error"):
            merged_item["scraper_error"] = r["error"]
        merged_by_casa[casa] = merged_item

    return list(merged_by_casa.values())

# 2.5) Last known: cargar/guardar último valor válido (auto)
def load_last_known(path="data/last_known_tasas.json"):
    """
    Devuelve (last_map, updated_at)
    last_map["Rextie"] = {"casa":..., "url":..., "compra":..., "venta":..., "last_seen":"YYYY-MM-DD"}
    """
    p = Path(path)
    if not p.exists():
        return {}, None

    data = json.loads(p.read_text(encoding="utf-8"))
    updated_at = data.get("updated_at")
    casas = data.get("casas", {})
    if not isinstance(casas, dict):
        casas = {}
    return casas, updated_at


def save_last_known(last_map, path="data/last_known_tasas.json"):
    """
    Guarda last_map en disco.
    """
    payload = {
        "updated_at": str(date.today()),
        "casas": last_map
    }
    os.makedirs(Path(path).parent, exist_ok=True)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def update_last_known_from_scraper_results(raw_results, last_map):
    """
    Recorre resultados crudos de scrapers y si una casa tiene compra/venta válidos,
    actualiza last_map[casa] con esos valores (y last_seen=hoy).
    """
    hoy = str(date.today())
    for r in raw_results:
        if not isinstance(r, dict):
            continue
        casa = r.get("casa")
        if not casa:
            continue
        if is_valid_rate(r):
            last_map[casa] = {
                "casa": casa,
                "url": r.get("url"),
                "compra": r.get("compra"),
                "venta": r.get("venta"),
                "last_seen": hoy
            }
    return last_map

# 3) MAIN: ejecuta scrapers, aplica backup, guarda tasas, histórico
async def main():
    run_at = datetime.now(timezone.utc).isoformat(timespec="minutes")

    # ---- Lista de scrapers (ordenados) ----
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

    # ---- Ejecutar scrapers secuencialmente (más estable) ----
    resultados = []
    for name, coro in tasks:
        resultados.append(await _safe_call(name, coro))

    # ---- Limpiar resultados (quitar None / cosas raras) ----
    resultados_raw = [r for r in resultados if isinstance(r, dict)]

    # ---- Cargar last known ----
    last_map, last_updated_at = load_last_known("data/last_known_tasas.json")

    # ---- Actualizar last known con los scrapers que salieron bien HOY ----
    last_map = update_last_known_from_scraper_results(resultados_raw, last_map)
    save_last_known(last_map, "data/last_known_tasas.json")
    print("💾 Last-known actualizado (data/last_known_tasas.json)")

    # ---- Cargar backup manual ----
    backup_map, fecha_backup = load_backup_map("data/backup_tasas.json")

    # ---- Aplicar fallbacks: scraper > last_known > backup > missing ----
    resultados = apply_fallbacks(resultados_raw, last_map, backup_map, fecha_backup)
    print(f"🧩 Fallbacks aplicados (backup_fecha={fecha_backup}, last_known_updated_at={last_updated_at})")

    # ---- Guardar tasas finales (scraper + backup) ----
    os.makedirs("data", exist_ok=True)
    with open("data/tasas.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print("✅ Tasas guardadas en data/tasas.json")

    meta = {
        "run_at_utc": run_at,
        "run_date": str(date.today()),
        "total": len(resultados),
        "ok_scraper": sum(1 for r in resultados if isinstance(r, dict) and r.get("source") == "scraper"),
        "fallback_last_known": sum(1 for r in resultados if isinstance(r, dict) and r.get("source") == "last_known"),
        "fallback_backup": sum(1 for r in resultados if isinstance(r, dict) and r.get("source") == "backup"),
        "missing": sum(1 for r in resultados if isinstance(r, dict) and r.get("source") == "missing"),
    }

    with open("data/meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("🧾 Meta guardada en data/meta.json")


    # 4) HISTÓRICO SUNAT (solo toma SUNAT y lo guarda por fecha)
    sunat_data = next((r for r in resultados_raw if r.get("casa") == "SUNAT"), None)
    if sunat_data and sunat_data.get("compra") and sunat_data.get("venta"):
        sunat_compra = sunat_data["compra"]
        sunat_venta = sunat_data["venta"]
        hoy = str(date.today())

        historico_path = "data/historico.json"

        # Leer histórico actual
        if os.path.exists(historico_path):
            with open(historico_path, "r", encoding="utf-8") as f:
                historico = json.load(f)
                if not isinstance(historico, list):
                    historico = []
        else:
            historico = []

        # Evitar duplicar el mismo día
        historico = [d for d in historico if isinstance(d, dict) and d.get("fecha") != hoy]
        historico.append({"fecha": hoy, "compra": sunat_compra, "venta": sunat_venta})

        # Guardar histórico
        with open(historico_path, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)

        print(f"📈 Histórico SUNAT actualizado: {hoy} Compra {sunat_compra} / Venta {sunat_venta}")
    else:
        print("⚠️ SUNAT no devolvió datos válidos. Se deja histórico sin cambios.")


if __name__ == "__main__":
    asyncio.run(main())