// ==============================
// File: scripts/ui/conversor.js
// ==============================

import { state, isReadySunat } from '../state.js';
import { $ } from './dom.js';
import { moneyFmt } from './format.js';

/* ============================================================
   Resultado conversor (TU fórmula intacta)
   + extra: muestra ahorro si existe en winner-row
   ============================================================ */
export function renderResultadoConversor() {
  const out = $('#resultado-modern');
  if (!out) return;

  const { modo, monto, monedaTengo, monedaQuiero, sunat } = state;
  let texto = '';

  if (!isReadySunat()) {
    texto = 'No hay tipo de cambio disponible (SUNAT).';
  } else if (!Number.isFinite(monto) || monto <= 0) {
    texto = 'Por favor ingresa un monto válido.';
  } else if (monedaTengo === monedaQuiero) {
    texto = 'Selecciona monedas diferentes.';
  }
  // MODO: RECIBIR
  else if (modo === 'recibir') {
    if (monedaTengo === 'USD') texto = `Recibirás S/${(monto * sunat.venta).toFixed(2)} soles.`;
    else texto = `Recibirás $${(monto / sunat.compra).toFixed(2)} dólares.`;
  }
  // MODO: NECESITO
  else {
    if (monedaTengo === 'USD') texto = `Necesitas S/${(monto * sunat.compra).toFixed(2)} soles para recibir $${monto}.`;
    else texto = `Necesitas $${(monto / sunat.venta).toFixed(2)} dólares para recibir S/${monto}.`;
  }

  // Extra: si el renderTabla dejó un ahorro estimado en la winner-row, lo añadimos
  const winner = document.querySelector('tr.winner-row');
  if (winner?.dataset?.ahorroVal && winner?.dataset?.ahorroCur) {
    const diff = parseFloat(winner.dataset.ahorroVal);
    const cur = winner.dataset.ahorroCur;
    if (Number.isFinite(diff)) {
      const sign = diff >= 0 ? 'Ahorras' : 'Pierdes';
      texto += ` · ${sign} ${moneyFmt(Math.abs(diff), cur)}`;
    }
  }

  out.textContent = texto;
}

export function syncMontoUI() {
  const prefix = $('#prefix-monto');
  const input = $('#monto');
  if (!prefix || !input) return;

  // prefijo según moneda que tengo
  const isPEN = state.monedaTengo === 'PEN';
  prefix.textContent = isPEN ? 'S/' : '$';

  // placeholder “Ej: 100”
  input.placeholder = 'Ej: 100';
}