// ==============================
// File: scripts/ui/savings.js
// ==============================

import { state, isReadySunat } from '../state.js';
import { getHaveWant } from './haveWant.js';

/* ============================================================
   Ahorro estimado (solo modo recibir)
   - Se calcula SOLO para la winner-row
   - NO altera tus cálculos
   ============================================================ */

export function attachAhorroToWinnerRow() {
  if (!isReadySunat() || !Number.isFinite(state.monto) || state.monto <= 0) return;

  const winnerRow = document.querySelector('tr.winner-row');
  if (!winnerRow) return;

  const casaName = winnerRow.querySelector('.casa-name')?.textContent?.trim();
  if (!casaName) return;

  const casa = state.validas.find(x => x.casa === casaName);
  if (!casa) return;

  const { have, want } = getHaveWant();

  let diff = null;
  let cur  = null;

  // =========================
  // MODO: RECIBIR
  // =========================
  if (state.modo === 'recibir') {

    // USD -> PEN
    if (have === 'USD' && want === 'PEN') {
      diff = (state.monto * casa.compra) - (state.monto * state.sunat.compra);
      cur = 'PEN';
    }

    // PEN -> USD
    if (have === 'PEN' && want === 'USD') {
      diff = (state.monto / casa.venta) - (state.monto / state.sunat.venta);
      cur = 'USD';
    }
  }

  // =========================
  // MODO: NECESITO
  // =========================
  if (state.modo === 'necesito') {

    // Quiero USD, pago PEN
    if (have === 'PEN' && want === 'USD') {
      diff = (state.monto * casa.venta) - (state.monto * state.sunat.venta);
      cur = 'PEN';
    }

    // Quiero PEN, pago USD
    if (have === 'USD' && want === 'PEN') {
      diff = (state.monto / casa.compra) - (state.monto / state.sunat.compra);
      cur = 'USD';
    }
  }

  if (Number.isFinite(diff) && cur) {
    winnerRow.dataset.ahorroCur = cur;
    winnerRow.dataset.ahorroVal = String(diff);
  }
}
