// ==============================
// File: scripts/ui/bestDeal.js
// ==============================
import { state } from '../state.js';
import { getHaveWant } from './haveWant.js';
import { rateFmt, moneyFmt } from './format.js';
import { getCasaLogoSrc } from './logos.js';

// ⚠️ GitHub Pages: si tu repo es /precio-dolar-hoy/, pon '/precio-dolar-hoy/'
const BASE_PATH = '';

export function renderBestDeal() {
  // IDs reales de tu HTML ✅
  const nameEl = document.getElementById('best-name');
  const buyEl  = document.getElementById('best-buy');
  const sellEl = document.getElementById('best-sell');
  const noteEl = document.getElementById('best-note');
  const btnEl  = document.getElementById('btn-ir-mejor');
  const logoEl = document.getElementById('best-logo'); // en tu HTML sí existe

  if (!nameEl || !buyEl || !sellEl) return;

  const filas = Array.isArray(state.validas) ? state.validas : [];

  // Estado vacío
  if (!filas.length) {
    nameEl.textContent = '—';
    buyEl.textContent = '—';
    sellEl.textContent = '—';
    if (noteEl) noteEl.textContent = '';
    if (btnEl) {
      btnEl.disabled = true;
      btnEl.textContent = 'Ir';
      btnEl.onclick = null;
    }
    if (logoEl) {
      logoEl.removeAttribute('src');
      logoEl.setAttribute('alt', '');
    }
    return;
  }

  const { modo } = state;
  const { have, want } = getHaveWant();

  const paintCompra =
    (modo === 'recibir'  && have === 'USD' && want === 'PEN') ||
    (modo === 'necesito' && want === 'PEN' && have === 'USD');

  const paintVenta =
    (modo === 'recibir'  && have === 'PEN' && want === 'USD') ||
    (modo === 'necesito' && want === 'USD' && have === 'PEN');

  // Ganador igual que la tabla:
  // - si importa compra: mayor compra
  // - si importa venta: menor venta
  let winner = null;

  if (paintCompra) {
    winner = filas.reduce((best, x) => {
      if (!best) return x;
      return (x.compra ?? -Infinity) > (best.compra ?? -Infinity) ? x : best;
    }, null);
  } else if (paintVenta) {
    winner = filas.reduce((best, x) => {
      if (!best) return x;
      return (x.venta ?? Infinity) < (best.venta ?? Infinity) ? x : best;
    }, null);
  } else {
    // fallback: usa el primero (si tu tabla ya viene ordenada, coincide)
    winner = filas[0] || null;
  }

  if (!winner) {
    nameEl.textContent = '—';
    buyEl.textContent = '—';
    sellEl.textContent = '—';
    if (noteEl) noteEl.textContent = '';
    if (logoEl) {
      logoEl.removeAttribute('src');
      logoEl.setAttribute('alt', '');
    }
    return;
  }

  // Pintar datos
  nameEl.textContent = winner.casa || '—';
  buyEl.textContent  = rateFmt(winner.compra);
  sellEl.textContent = rateFmt(winner.venta);

  // Nota: usa ahorro si existe (lo setea savings.js en winner-row)
  if (noteEl) {
    const row = document.querySelector('tr.winner-row');
    const diff = row?.dataset?.ahorroVal ? parseFloat(row.dataset.ahorroVal) : NaN;
    const cur  = row?.dataset?.ahorroCur || '';

    if (Number.isFinite(diff) && cur) {
      const verb = diff >= 0 ? 'Ahorras' : 'Pierdes';
      noteEl.textContent = `${verb} ${moneyFmt(Math.abs(diff), cur)} frente al promedio.`;
    } else {
      noteEl.textContent = 'Mejor opción según el tipo de cambio.';
    }
  }

  // Logo
  if (logoEl) {
    const raw = getCasaLogoSrc(winner.casa);
    const src = raw ? (BASE_PATH + raw.replace(/^\//, '')) : '';

    if (src) {
      logoEl.src = src;
      logoEl.setAttribute('alt', winner.casa ? `Logo de ${winner.casa}` : 'Logo');
    } else {
      logoEl.removeAttribute('src');
      logoEl.setAttribute('alt', '');
    }
  }

  // Botón ir a la casa
  if (btnEl) {
    const hasUrl = Boolean(winner.url);

    btnEl.disabled = !hasUrl;

    // Si estás haciendo “logo-first”, este texto se ve más limpio:
    // (si prefieres el anterior, cambia por: `Ir a ${winner.casa}`)
    btnEl.textContent = hasUrl ? `Ir a ${winner.casa}` : 'Ir';

    btnEl.onclick = hasUrl
      ? () => window.open(winner.url, '_blank', 'noopener')
      : null;
  }
}