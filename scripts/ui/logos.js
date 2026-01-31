// ==============================
// File: scripts/ui/logos.js
// ==============================

// 1) Mapa ORIGINAL (tal cual lo tienes)
const LOGO_BY_CASA = {
  'Acomo': '/IMG/casas/acomo.webp',
  'Billex': '/IMG/casas/billex.webp',
  'CambioSeguro': '/IMG/casas/cambioseguro.webp',
  'CambioX': '/IMG/casas/cambiox.webp',
  'Cambix': '/IMG/casas/cambix.webp',
  'ChapaCambio': '/IMG/casas/chapacambio.webp',
  'ChaskiDolar': '/IMG/casas/chaskidolar.webp',
  'Dichikash': '/IMG/casas/dichikash.webp',
  'DinersFX': '/IMG/casas/dinersfx.webp',
  'DlsMoney': '/IMG/casas/dlsmoney.webp',
  'Dolarex': '/IMG/casas/dolarex.webp',
  'DollarHouse': '/IMG/casas/dollarhouse.webp',
  'Global66': '/IMG/casas/global66.webp',
  'HirPower': '/IMG/casas/hirpower.webp',
  'InkaMoney': '/IMG/casas/inkamoney.webp',
  'InstaKash': '/IMG/casas/instakash.webp',
  'Intercambialo': '/IMG/casas/intercambialo.webp',
  'IntiCambio': '/IMG/casas/inticambio.webp',
  'JetPerú': '/IMG/casas/jetperu.webp',
  'KallpaCambios': '/IMG/casas/kallpacambios.webp',
  'Kambio': '/IMG/casas/kambioonline.webp',
  'Kambista': '/IMG/casas/kambista.webp',
  'MegaMoney': '/IMG/casas/megamoney.webp',
  'MidpointFX': '/IMG/casas/midpointfx.webp',
  'Okane': '/IMG/casas/okane.webp',
  'PeruDolar': '/IMG/casas/perudolar.webp',
  'Rextie': '/IMG/casas/rextie.webp',
  'Rissan': '/IMG/casas/rissan.webp',
  'Roblex': '/IMG/casas/roblex.webp',
  'Safex': '/IMG/casas/safex.webp',
  'Securex': '/IMG/casas/securex.webp',
  'SmartDollar': '/IMG/casas/smartdollar.webp',
  'SRCambio': '/IMG/casas/srcambio.webp',
  'SUNAT': '/IMG/casas/sunat.webp',
  'TKambio': '/IMG/casas/tkambio.webp',
  'TuCambista': '/IMG/casas/tucambista.webp',
  'WesternUnion': '/IMG/casas/westernunion.webp',
  'XCambio': '/IMG/casas/xcambio.webp',
  'Yanki': '/IMG/casas/yanki.webp',
  'ZonaDólar': '/IMG/casas/zonadolar.webp',
  'MercadoCambiario': '/IMG/casas/mercadocambiario.webp',
  'TraderPeruFX': '/IMG/casas/marketdollar.webp',
  'CambioDigitalPeru': '/IMG/casas/cambiodigital.webp',
  'CambioMas': '/IMG/casas/masssoluciones.webp',
  'CambiaFX': '/IMG/casas/cambiafx.webp',
  'VipCapital': '/IMG/casas/vipcapital.webp',
  'RissanPE': '/IMG/casas/rissan.webp',
  'CambioSol': '/IMG/casas/cambiosol.webp',
  'MoneyHouse': '/IMG/casas/moneyhouse.webp',
  'CambioMundial': '/IMG/casas/cambiomundial.webp',
};

// 2) Normalizador: hace match aunque tu data venga sin tildes, con espacios, etc.
function norm(s = '') {
  return s
    .toLowerCase()
    .normalize('NFD')                      // separa tildes
    .replace(/[\u0300-\u036f]/g, '')      // quita tildes
    .replace(/\s+/g, '')                  // quita espacios
    .replace(/[^a-z0-9]/g, '');           // quita símbolos raros
}

// 3) Índice normalizado (clave -> ruta)
const LOGO_BY_CASA_NORM = Object.fromEntries(
  Object.entries(LOGO_BY_CASA).map(([k, v]) => [norm(k), v])
);

// 4) Export: tu UI llamará esto
export function getCasaLogoSrc(nombreCasa) {
  if (!nombreCasa) return null;
  return LOGO_BY_CASA_NORM[norm(nombreCasa)] || null;
}

// (Opcional) export para debug
export function _debugLogos() {
  return { LOGO_BY_CASA, LOGO_BY_CASA_NORM };
}