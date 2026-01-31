// ==============================
// File: scripts/ui/table.js
// ==============================

import { state } from '../state.js';
import { $ } from './dom.js';
import { getHaveWant } from './haveWant.js';
import { moneyFmt, rateFmt } from './format.js';
import { getCasaLogoSrc } from './logos.js';
import { attachAhorroToWinnerRow } from './savings.js';

// ⚠️ IMPORTANTE (GitHub Pages)
// Si tu web vive en /NOMBRE-REPO/, pon BASE_PATH = '/NOMBRE-REPO/'.
// Si estás en dominio raíz, déjalo en ''.
const BASE_PATH = ''; // ejemplo: '/precio-dolar-hoy/'

/* ============================================================
   TABLA: render
   - Logos
   - Fila ganadora (winner-row)
   - Ahorro estimado para winner (solo en modo recibir)
   ============================================================ */
export function renderTabla() {
  const tbody = $('#tablaCuerpo');
  if (!tbody) return;
  tbody.innerHTML = '';

  let filas = ordenarValidasSegunModo();

  // ✅ Quitar SUNAT de la tabla (SUNAT no es casa de cambio)
  filas = filas.filter(c => (c.slug ?? '').toLowerCase() !== 'sunat' && String(c.casa).toUpperCase() !== 'SUNAT');

  // ✅ Nuevo toggle: checked = Ver todas (muestra todas + scroll)
  const chk = $('#solo-verificadas');
  const showAll = chk ? !!chk.checked : false;

  // wrapper scroll solo si showAll
  const wrap = document.querySelector('.tabla-casas-wrapper.tabla-casas-wrapper--wide');
  if (wrap) wrap.classList.toggle('is-all', showAll);

  // si NO es showAll, recorta a top N
  const TOP_N = 3; // cambia a 4 si quieres
  if (!showAll) filas = filas.slice(0, TOP_N);

  // ============================
  // DEFINIR QUÉ SE PINTA (tu lógica intacta)
  // ============================
  const { modo } = state;
  const { have, want } = getHaveWant();

  let bestCompra = null;
  let worstCompra = null;
  let bestVenta = null;
  let worstVenta = null;

  const paintCompra =
    (modo === 'recibir' && have === 'USD' && want === 'PEN') ||
    (modo === 'necesito' && want === 'PEN' && have === 'USD');

  const paintVenta =
    (modo === 'recibir' && have === 'PEN' && want === 'USD') ||
    (modo === 'necesito' && want === 'USD' && have === 'PEN');

  // USD → PEN => COMPRA importa (más alta = mejor)
  if (paintCompra && filas.length) {
    bestCompra = Math.max(...filas.map(c => c.compra));
    worstCompra = Math.min(...filas.map(c => c.compra));
  }

  // PEN → USD => VENTA importa (más baja = mejor)
  if (paintVenta && filas.length) {
    bestVenta = Math.min(...filas.map(c => c.venta));
    worstVenta = Math.max(...filas.map(c => c.venta));
  }

  // ============================
  // Winner casa (para resaltar 1 opción)
  // ============================
  let winnerCasa = null;

  if (paintCompra && bestCompra != null) {
    winnerCasa = (filas.find(x => x.compra === bestCompra))?.casa || null;
  }
  if (paintVenta && bestVenta != null) {
    winnerCasa = (filas.find(x => x.venta === bestVenta))?.casa || null;
  }

  // (Opcional) debug: casas sin logo
  const missing = new Set();

  // ============================
  // Render filas
  // ============================
  for (const c of filas) {
    const tr = document.createElement('tr');
    tr.className = 'fila-casa';
    tr.dataset.compra = c.compra;
    tr.dataset.venta = c.venta;

    const isWinner = (winnerCasa && c.casa === winnerCasa);
    if (isWinner) tr.classList.add('winner-row');

    // Logo con normalizador + BASE_PATH para GH Pages
    const rawLogo = getCasaLogoSrc(c.casa);
    const logoSrc = rawLogo ? (BASE_PATH + rawLogo.replace(/^\//, '')) : null;
    if (!logoSrc) missing.add(c.casa);

    const casaCell = `
  <td class="casa">
    <a class="casa-wrap" href="${c.url}" target="_blank" rel="noopener">
      ${logoSrc ? `<span class="casa-logo"><img src="${logoSrc}" alt="${c.casa}" loading="lazy"></span>` : ''}
      <span class="casa-name">${c.casa}</span>
    </a>
  </td>
`;

    tr.innerHTML = `
      ${casaCell}

      <td class="compra
        ${paintCompra && c.compra === bestCompra ? 'mejor-compra' : ''}
        ${paintCompra && c.compra === worstCompra ? 'peor-compra' : ''}">
        ${rateFmt(c.compra)}
      </td>

      <td class="venta
        ${paintVenta && c.venta === bestVenta ? 'mejor-venta' : ''}
        ${paintVenta && c.venta === worstVenta ? 'peor-venta' : ''}">
        ${rateFmt(c.venta)}
      </td>

      <td class="dolares dolares-obtenidos">-</td>
      <td class="soles soles-recibidos">-</td>
    `;

    tbody.appendChild(tr);
  }

  if (missing.size) {
    console.log('Casas sin logo (por nombre no coincide o ruta falla):', [...missing]);
  }

  actualizarEncabezadosTabla();
  recalcularCeldas();

  // ✅ ahora viene de savings.js
  attachAhorroToWinnerRow();
}

/* ============================================================
   Ordenar validas (tu lógica intacta)
   ============================================================ */
function ordenarValidasSegunModo() {
  const { validas, modo } = state;
  const arr = [...validas];

  const { have, want } = getHaveWant();

  if (modo === 'recibir') {
    if (have === 'USD' && want === 'PEN') {
      arr.sort((a, b) => b.compra - a.compra);
    } else if (have === 'PEN' && want === 'USD') {
      arr.sort((a, b) => a.venta - b.venta);
    }
  } else {
    if (want === 'USD' && have === 'PEN') {
      arr.sort((a, b) => a.venta - b.venta);
    } else if (want === 'PEN' && have === 'USD') {
      arr.sort((a, b) => b.compra - a.compra);
    }
  }

  return arr;
}

/* ============================================================
   Encabezados tabla (tu lógica intacta)
   ============================================================ */
function actualizarEncabezadosTabla() {
  const thD = $('#columna-dolares');
  const thS = $('#columna-soles');
  const tengo = state.monedaTengo === 'USD' ? 'dolares' : 'soles';

  if (!thD || !thS) return;
  thD.textContent = 'Dólares';
  thS.textContent = 'Soles';

  if (state.modo === 'recibir') {
    if (tengo === 'soles') thD.textContent = 'Dólares recibidos';
    if (tengo === 'dolares') thS.textContent = 'Soles recibidos';
  } else {
    if (tengo === 'dolares') thS.textContent = 'Soles necesarios';
    if (tengo === 'soles') thD.textContent = 'Dólares necesarios';
  }
}

/* ============================================================
   Recalcular celdas (TU fórmula intacta)
   ============================================================ */
export function recalcularCeldas() {
  const { monto, modo } = state;
  if (!monto || monto <= 0) return;

  const { have, want } = getHaveWant();

  document.querySelectorAll('.fila-casa').forEach(fila => {
    const compra = parseFloat(fila.dataset.compra);
    const venta = parseFloat(fila.dataset.venta);

    const celD = fila.querySelector('.dolares-obtenidos');
    const celS = fila.querySelector('.soles-recibidos');

    celD.textContent = '-';
    celS.textContent = '-';

    if (!Number.isFinite(compra) || !Number.isFinite(venta)) return;

    if (modo === 'recibir') {
      if (have === 'PEN' && want === 'USD') {
        celD.textContent = moneyFmt(monto / venta, 'USD');
      } else if (have === 'USD' && want === 'PEN') {
        celS.textContent = moneyFmt(monto * compra, 'PEN');
      }
    } else {
      if (want === 'USD' && have === 'PEN') {
        celS.textContent = moneyFmt(monto * venta, 'PEN');
      } else if (want === 'PEN' && have === 'USD') {
        celD.textContent = moneyFmt(monto / compra, 'USD');
      }
    }
  });
}