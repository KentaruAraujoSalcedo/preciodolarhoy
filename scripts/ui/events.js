// ==============================
// File: scripts/ui/events.js
// ==============================

import { setState } from '../state.js';
import { $, $$ } from './dom.js';
import { updateLabels, ensureOppositeSelect, syncAdornmentAndChips } from './labels.js';

export function bindEvents({ onChange }) {
  const montoEl = $('#monto');
  const selTengo = $('#moneda-tengo');   // ahora está oculto (sr-only), pero sigue existiendo
  const selQuiero = $('#moneda-quiero'); // ahora está oculto (sr-only), pero sigue existiendo

  // Pills visibles (UI PRO)
  const curHave = $('#cur-have');
  const curWant = $('#cur-want');

  // Helper: setea monto SIEMPRE en número
  function setMontoFromInput() {
    if (!montoEl) return;
    const v = parseFloat(montoEl.value);
    setState({ monto: Number.isFinite(v) ? v : 0 });
  }

  // Helper: pinta la línea PRO (USD ⇄ PEN)
  function paintCurrencyLine() {
    if (!curHave || !curWant || !selTengo || !selQuiero) return;

    curHave.textContent = selTengo.value === 'USD' ? 'Dólares (USD)' : 'Soles (PEN)';
    curWant.textContent = selQuiero.value === 'USD' ? 'Dólares (USD)' : 'Soles (PEN)';
  }

  // Radios (modo)
  $$('input[name="modo"]').forEach(r => {
    r.addEventListener('change', () => {
      setState({ modo: r.value });
      updateLabels();
      syncAdornmentAndChips();
      onChange();
    });
  });

  // ✅ Monto (sin debounce, inmediato)
  montoEl?.addEventListener('input', () => {
    setMontoFromInput();
    syncAdornmentAndChips();
    onChange();
  });

  // ✅ Chips rápidos (dispara input para que todo siga el mismo flujo)
  $$('.quick-amt').forEach(btn => {
    btn.addEventListener('click', () => {
      const v = parseFloat(btn.dataset.amt);
      if (!Number.isFinite(v) || !montoEl) return;

      montoEl.value = String(v);
      montoEl.dispatchEvent(new Event('input', { bubbles: true }));
    });
  });

  // ✅ Botón invertir (control principal de monedas en UI PRO)
  const btnSwap = $('#btn-swap');
  btnSwap?.addEventListener('click', () => {
    if (!selTengo || !selQuiero) return;

    // 1️⃣ Invertimos "tengo" y forzamos "quiero" a ser el opuesto
    selTengo.value = selTengo.value === 'USD' ? 'PEN' : 'USD';
    ensureOppositeSelect(selTengo, selQuiero);

    setState({
      monedaTengo: selTengo.value,
      monedaQuiero: selQuiero.value
    });

    // 2️⃣ ✨ Animación PRO del swap (micro–interacción)
    const line = document.querySelector('.currency-line');
    line?.classList.add('is-swap');
    setTimeout(() => line?.classList.remove('is-swap'), 220);

    // 3️⃣ Sincronizar UI y cálculos
    updateLabels();
    syncAdornmentAndChips();
    setMontoFromInput();

    paintCurrencyLine();
    onChange();
  });


  // Pintado inicial (por si state inicial cambió)
  paintCurrencyLine();

  // Botón calcular (si existe)
  const btnCalc = $('#btn-calcular');
  btnCalc?.addEventListener('click', () => {
    setMontoFromInput();
    syncAdornmentAndChips();
    onChange();
  });

  // Toggle “Top 5” (checked = Top 5, unchecked = todas)
  const only = $('#solo-verificadas');
  only?.addEventListener('change', () => {
    setState({ topOnly: !!only.checked });
    onChange();
  });


}
