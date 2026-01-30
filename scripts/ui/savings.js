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

  // Solo en “recibir”
  if (state.modo !== 'recibir') return;

  const { have, want } = getHaveWant();

  // Caso A: USD -> PEN (casa usa COMPRA; SUNAT según tu conversor usa venta)
  if (have === 'USD' && want === 'PEN') {
    const solesCasa = state.monto * casa.compra;
    const solesSunat = state.monto * state.sunat.venta;
    winnerRow.dataset.ahorroCur = 'PEN';
    winnerRow.dataset.ahorroVal = String(solesCasa - solesSunat);
    return;
  }

  // Caso B: PEN -> USD (casa usa VENTA; SUNAT según tu conversor usa compra)
  if (have === 'PEN' && want === 'USD') {
    const usdCasa = state.monto / casa.venta;
    const usdSunat = state.monto / state.sunat.compra;
    winnerRow.dataset.ahorroCur = 'USD';
    winnerRow.dataset.ahorroVal = String(usdCasa - usdSunat);
  }
}