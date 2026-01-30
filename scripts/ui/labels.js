// ==============================
// File: scripts/ui/labels.js
// ==============================

import { state } from '../state.js';
import { $ } from './dom.js';

export function updateLabels() {
  const labelMonto = $('#label-monto');
  const labelConvertir = $('#label-convertir');
  const labelMonedaTengo = $('#label-moneda-tengo');
  const { modo } = state;

  if (!labelMonto || !labelConvertir || !labelMonedaTengo) return;

  if (modo === 'recibir') {
    labelMonto.textContent = 'Tengo';
    labelMonedaTengo.textContent = 'Moneda';
    labelConvertir.textContent = 'Quiero en';
  } else {
    labelMonto.textContent = 'Quiero';
    labelMonedaTengo.textContent = 'Moneda';
    labelConvertir.textContent = 'Tengo en';
  }
}

export function ensureOppositeSelect(origen, destino) {
  if (!origen || !destino) return;
  destino.value = origen.value === 'USD' ? 'PEN' : 'USD';
}

export function syncAdornmentAndChips() {
  const selTengo = document.getElementById('moneda-tengo');
  const chips = document.querySelectorAll('.quick-amt');
  const adorn = document.querySelector('.input-with-icon .icon-left');

  const isPEN = selTengo?.value === 'PEN';
  if (adorn) adorn.textContent = isPEN ? 'S/' : '$';

  chips.forEach(btn => {
    const v = btn.dataset.amt;
    btn.textContent = (isPEN ? 'S/ ' : '$ ') + Number(v).toLocaleString('es-PE');
  });
}