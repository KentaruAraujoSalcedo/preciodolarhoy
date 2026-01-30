// ==============================
// File: scripts/data.js
// ==============================
import { state, setState } from './state.js';

/* ============================================================
   Helpers de normalización (para logos / matching / filtros)
   ============================================================ */

// Convierte "ZonaDólar", "Zona Dolar", "zona-dólar" => "zonadolar"
function slugCasa(nombre = '') {
  return String(nombre)
    .trim()
    .toLowerCase()
    .normalize('NFD')                 // separa acentos
    .replace(/[\u0300-\u036f]/g, '')  // elimina acentos
    .replace(/[^a-z0-9]+/g, '')       // deja solo alfanumérico
}

// Lista “baseline” de casas verificadas (ajústala a tu gusto)
const VERIFIED_SLUGS = new Set([
  'sunat',
  'zonadolar',
  'inkamoney',
  'chaskidolar',
  // agrega las que tú consideres verificadas
]);

// Carga tasas y separa válidas/ inválidas. No toca el DOM aquí.
export async function cargarTasas() {
  const res = await fetch('data/tasas.json');
  const todasRaw = await res.json();

  // Enriquecemos cada casa con:
  // - slug: para match con logos, consistencia, etc.
  // - verificada: para el toggle "Solo verificadas"
  const todas = todasRaw.map(c => {
    const slug = slugCasa(c.casa);

    return {
      ...c,
      slug,                              // útil para logos
      verificada: VERIFIED_SLUGS.has(slug) // útil para filtro
    };
  });

  const validas = todas.filter(c => Number.isFinite(c.compra) && Number.isFinite(c.venta));
  const invalidas = todas.filter(c => !Number.isFinite(c.compra) || !Number.isFinite(c.venta));

  // “mejores” globales (sin modo)
  const mejorCompra = validas.length ? Math.max(...validas.map(c => c.compra)) : null;
  const mejorVenta  = validas.length ? Math.min(...validas.map(c => c.venta))  : null;

  // Winner global (sirve para badge/CTA; el modo final lo decide UI)
  // Ojo: esto es “mejor compra” por defecto. UI puede redefinir según modo.
  const winnerCompra = (mejorCompra != null)
    ? validas.find(c => c.compra === mejorCompra)?.casa ?? null
    : null;

  const winnerVenta = (mejorVenta != null)
    ? validas.find(c => c.venta === mejorVenta)?.casa ?? null
    : null;

  setState({
    tasas: todas,
    validas,
    invalidas,
    mejorCompra,
    mejorVenta,
    winnerCompra,
    winnerVenta
  });
}

export async function cargarSunatDesdeTasas() {
  // Busca SUNAT dentro del mismo JSON de tasas
  if (!state.tasas.length) await cargarTasas();

  // Soporta variaciones del nombre (SUNAT, Sunat, etc.)
  const sunat = state.tasas.find(t => slugCasa(t.casa) === 'sunat');

  if (sunat && Number.isFinite(sunat.compra) && Number.isFinite(sunat.venta)) {
    setState({ sunat: { compra: sunat.compra, venta: sunat.venta } });
  } else {
    setState({ sunat: { compra: null, venta: null } });
  }
}

export async function cargarHistorico() {
  const res = await fetch('data/historico.json');
  const data = await res.json();

  // Orden por fecha asc y últimos 7
  return data
    .sort((a, b) => new Date(a.fecha) - new Date(b.fecha))
    .slice(-7);
}

// ==============================
// META (cuándo corrieron los scrapers)
// ==============================
export async function cargarMeta() {
  try {
    const res = await fetch('data/meta.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`meta.json ${res.status}`);
    const meta = await res.json();

    // lo guardamos en state por si lo quieres usar luego (badge, debug, etc.)
    setState({ meta });

    return meta;
  } catch (e) {
    console.warn('Meta no disponible:', e);
    setState({ meta: null });
    return null;
  }
}
