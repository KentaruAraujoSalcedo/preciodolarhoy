// ==============================
// File: scripts/data.js
// ==============================
import { state, setState } from './state.js';

// Carga tasas y separa válidas/ inválidas. No toca el DOM aquí.
export async function cargarTasas() {
  const res = await fetch('data/tasas.json');
  const todas = await res.json();
  const validas = todas.filter(c => Number.isFinite(c.compra) && Number.isFinite(c.venta));
  const invalidas = todas.filter(c => !Number.isFinite(c.compra) || !Number.isFinite(c.venta));

  const mejorCompra = validas.length ? Math.max(...validas.map(c => c.compra)) : null;
  const mejorVenta  = validas.length ? Math.min(...validas.map(c => c.venta))  : null;

  setState({ tasas: todas, validas, invalidas, mejorCompra, mejorVenta });
}

export async function cargarSunatDesdeTasas() {
  // Busca SUNAT dentro del mismo JSON de tasas
  if (!state.tasas.length) await cargarTasas();
  const sunat = state.tasas.find(t => t.casa === 'SUNAT');
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
  return data.sort((a, b) => new Date(a.fecha) - new Date(b.fecha)).slice(-7);
}