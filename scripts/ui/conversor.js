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
    // Tengo USD -> recibo PEN: uso COMPRA
    if (monedaTengo === 'USD') {
      texto = `Recibirías aproximadamente ${moneyFmt(monto * sunat.compra, 'PEN')} según SUNAT.`;
    }
    // Tengo PEN -> recibo USD: uso VENTA
    else {
      texto = `Recibirías aproximadamente ${moneyFmt(monto / sunat.venta, 'USD')} según SUNAT.`;
    }
  }

  // MODO: NECESITO
  else {
    // Tengo PEN (quiero USD): necesito PEN pagando VENTA
    if (monedaTengo === 'PEN') {
      texto = `Necesitarías aproximadamente ${moneyFmt(monto / sunat.compra, 'USD')} según SUNAT.`;
    }
    // Tengo USD (quiero PEN): necesito USD usando COMPRA
    else {
      texto = `Necesitarías aproximadamente ${moneyFmt(monto * sunat.venta, 'PEN')} según SUNAT.`;
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