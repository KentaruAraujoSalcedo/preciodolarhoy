// ==============================
// File: scripts/ui/static.js
// ==============================

import { $ } from './dom.js';
import { ensureOppositeSelect, syncAdornmentAndChips } from './labels.js';
import { initSunatModal } from './modal.js'; // ✅ NUEVO

export function initStaticUI() {
  // ✅ Modal SUNAT (abrir/cerrar)
  initSunatModal();

  // Fecha
  const fechaEl = $('#fecha');
  if (fechaEl) {
    fechaEl.textContent = new Date().toLocaleDateString('es-PE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }

  // Hora
  const horaEl = $('#hora');
  if (horaEl) {
    horaEl.textContent = new Date().toLocaleTimeString('es-PE', {
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  // Moneda quiero siempre opuesta a tengo
  const selTengo = $('#moneda-tengo');
  const selQuiero = $('#moneda-quiero');
  if (selTengo && selQuiero) {
    selQuiero.disabled = true; // controlado por JS
    ensureOppositeSelect(selTengo, selQuiero);
  }

  // Símbolo/chips coherentes
  syncAdornmentAndChips();
}
