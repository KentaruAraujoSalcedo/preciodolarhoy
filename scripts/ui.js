// ==============================
// File: scripts/ui.js
// ==============================

// Funcion Helper:
function getHaveWant() {
  const { modo, monedaTengo, monedaQuiero } = state;

  // En recibir: (tengo -> quiero)
  // En necesito: (quiero -> tengo)  ← se invierte
  const have = (modo === 'recibir') ? monedaTengo : monedaQuiero;
  const want = (modo === 'recibir') ? monedaQuiero : monedaTengo;

  return { have, want };
}

import { state, setState, isReadySunat } from './state.js';

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

export function initStaticUI() {
  // Fecha
  const fechaEl = $('#fecha');
  if (fechaEl) {
    fechaEl.textContent = new Date().toLocaleDateString('es-PE', {
      year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  // Hora
  const horaEl = $('#hora');
  if (horaEl) {
    horaEl.textContent = new Date().toLocaleTimeString('es-PE', {
      hour: '2-digit', minute: '2-digit'
    });
  }


  // Moneda quiero siempre opuesta a tengo
  const selTengo = $('#moneda-tengo');
  const selQuiero = $('#moneda-quiero');
  if (selTengo && selQuiero) {
    selQuiero.disabled = true; // controlado por JS
    ensureOppositeSelect(selTengo, selQuiero);
  }
  // ⬇️ nuevo
  syncAdornmentAndChips();
}


export function bindEvents({ onChange }) {
  // --- Radios (modo) ---
  $$('input[name="modo"]').forEach(r => {
    r.addEventListener('change', () => {
      setState({ modo: r.value });
      updateLabels();
      syncAdornmentAndChips();   // ⬅ actualiza símbolo/chips
      onChange();
    });
  });

  // --- Monto (con pequeño debounce) ---
  const montoEl = $('#monto');
  let t;
  montoEl?.addEventListener('input', () => {
    clearTimeout(t);
    t = setTimeout(() => {
      const v = parseFloat(montoEl.value);
      setState({ monto: Number.isFinite(v) ? v : 0 });
      onChange();
    }, 120);
  });

  // --- Selects moneda ---
  const selTengo = $('#moneda-tengo');
  const selQuiero = $('#moneda-quiero');

  selTengo?.addEventListener('change', () => {
    ensureOppositeSelect(selTengo, selQuiero);
    setState({ monedaTengo: selTengo.value, monedaQuiero: selQuiero.value });
    syncAdornmentAndChips();     // ⬅ actualiza símbolo/chips
    onChange();
  });

  selQuiero?.addEventListener('change', () => { // por si luego lo habilitas
    ensureOppositeSelect(selQuiero, selTengo);
    setState({ monedaTengo: selTengo.value, monedaQuiero: selQuiero.value });
    syncAdornmentAndChips();     // ⬅ por coherencia
    onChange();
  });

  // --- Chips rápidos de monto ---
  $$('.quick-amt').forEach(btn => {
    btn.addEventListener('click', () => {
      const v = parseFloat(btn.dataset.amt);
      if (Number.isFinite(v)) {
        setState({ monto: v });
        const inp = $('#monto'); if (inp) inp.value = v;
        onChange();
      }
    });
  });

  // --- Botón invertir monedas ---
  const btnSwap = $('#btn-swap');
  if (btnSwap) {
    btnSwap.addEventListener('click', () => {
      // Usamos las mismas refs, no hace falta redeclararlas
      if (!selTengo || !selQuiero) return;
      selTengo.value = selTengo.value === 'USD' ? 'PEN' : 'USD';
      ensureOppositeSelect(selTengo, selQuiero);
      setState({ monedaTengo: selTengo.value, monedaQuiero: selQuiero.value });
      syncAdornmentAndChips();   // ⬅ actualiza símbolo/chips
      onChange();
    });
  }

  // --- (opcional) Botón calcular: dispara el mismo onChange ---
  const btnCalc = $('#btn-calcular');
  btnCalc?.addEventListener('click', () => {
    const v = parseFloat($('#monto')?.value);
    setState({ monto: Number.isFinite(v) ? v : 0 });
    onChange();
  });
}


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

// --------- Tabla de casas ---------
const moneyFmt = (n, cur) => Number.isFinite(n)
  ? n.toLocaleString('es-PE', { style: 'currency', currency: cur })
  : '-';

const rateFmt = (n) => Number.isFinite(n) ? n.toFixed(3) : '–';

export function renderTabla() {
  const tbody = $('#tablaCuerpo');
  if (!tbody) return;
  tbody.innerHTML = '';

  const filas = ordenarValidasSegunModo();

  // ============================
// DEFINIR QUÉ SE PINTA (CORRECTO)
// ============================
const { modo } = state;
const { have, want } = getHaveWant();

let bestCompra = null;
let worstCompra = null;
let bestVenta = null;
let worstVenta = null;

const paintCompra =
  (modo === 'recibir'  && have === 'USD' && want === 'PEN') ||
  (modo === 'necesito' && want === 'PEN' && have === 'USD');

const paintVenta =
  (modo === 'recibir'  && have === 'PEN' && want === 'USD') ||
  (modo === 'necesito' && want === 'USD' && have === 'PEN');

  // USD → PEN => me compran USD => COMPRA importa
  if (paintCompra && filas.length) {
    bestCompra = Math.max(...filas.map(c => c.compra));
    worstCompra = Math.min(...filas.map(c => c.compra));
  }

  // PEN → USD => compro USD => VENTA importa
  if (paintVenta && filas.length) {
    bestVenta = Math.min(...filas.map(c => c.venta));
    worstVenta = Math.max(...filas.map(c => c.venta));
  }

  // ============================
  // RENDER DE FILAS
  // ============================
  for (const c of filas) {
    const tr = document.createElement('tr');
    tr.className = 'fila-casa';
    tr.dataset.compra = c.compra;
    tr.dataset.venta = c.venta;

    tr.innerHTML = `
      <td><a href="${c.url}" target="_blank">${c.casa}</a></td>

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

      <td class="dolares-obtenidos">-</td>
      <td class="soles-recibidos">-</td>
    `;

    tbody.appendChild(tr);
  }

  actualizarEncabezadosTabla();
  recalcularCeldas();
}

function ordenarValidasSegunModo() {
  const { validas, modo } = state;
  const arr = [...validas];

  const { have, want } = getHaveWant();

  if (modo === 'recibir') {
    if (have === 'USD' && want === 'PEN') {
      // soles recibidos = USD * COMPRA -> mejor COMPRA más alta
      arr.sort((a, b) => b.compra - a.compra);
    } else if (have === 'PEN' && want === 'USD') {
      // USD recibidos = PEN / VENTA -> mejor VENTA más baja
      arr.sort((a, b) => a.venta - b.venta);
    }
  } else {
    // necesito: monto está en WANT
    if (want === 'USD' && have === 'PEN') {
      // PEN necesarios = USD * VENTA -> mejor VENTA más baja
      arr.sort((a, b) => a.venta - b.venta);
    } else if (want === 'PEN' && have === 'USD') {
      // USD necesarios = PEN / COMPRA -> mejor COMPRA más alta
      arr.sort((a, b) => b.compra - a.compra);
    }
  }

  return arr;
}

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

export function recalcularCeldas() {
  const { monto, modo } = state;
  if (!monto || monto <= 0) return;

  const { have, want } = getHaveWant();

  document.querySelectorAll('.fila-casa').forEach(fila => {
    const compra = parseFloat(fila.dataset.compra);
    const venta  = parseFloat(fila.dataset.venta);

    const celD = fila.querySelector('.dolares-obtenidos');
    const celS = fila.querySelector('.soles-recibidos');

    celD.textContent = '-';
    celS.textContent = '-';

    if (!Number.isFinite(compra) || !Number.isFinite(venta)) return;

    if (modo === 'recibir') {
      // tengo -> quiero
      if (have === 'PEN' && want === 'USD') {
        // compro USD => uso VENTA
        celD.textContent = moneyFmt(monto / venta, 'USD');
      } else if (have === 'USD' && want === 'PEN') {
        // vendo USD => uso COMPRA
        celS.textContent = moneyFmt(monto * compra, 'PEN');
      }
    } else {
      // necesito: "monto" está en WANT (lo que quieres recibir)
      if (want === 'USD' && have === 'PEN') {
        // quiero USD, tengo PEN => PEN necesarios = USD * VENTA
        celS.textContent = moneyFmt(monto * venta, 'PEN');
      } else if (want === 'PEN' && have === 'USD') {
        // quiero PEN, tengo USD => USD necesarios = PEN / COMPRA
        celD.textContent = moneyFmt(monto / compra, 'USD');
      }
    }
  });
}

export function renderSunat() {
  const c = document.getElementById('sunat-compra');
  const v = document.getElementById('sunat-venta');
  if (!c || !v) return;

  if (isReadySunat()) {
    c.textContent = state.sunat.compra.toFixed(3);
    v.textContent = state.sunat.venta.toFixed(3);
  } else {
    c.textContent = '–';
    v.textContent = '–';
  }

  // Si existe mini-SUNAT en el conversor, actualízalo también
  const mc = document.getElementById('mini-c');
  const mv = document.getElementById('mini-v');
  if (mc && mv) {
    if (isReadySunat()) {
      mc.textContent = state.sunat.compra.toFixed(3);
      mv.textContent = state.sunat.venta.toFixed(3);
    } else {
      mc.textContent = '–';
      mv.textContent = '–';
    }
  }

}

export function renderResultadoConversor() {
  const out = document.getElementById('resultado-modern');
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
  // ======================
  // MODO: RECIBIR
  // ======================
  else if (modo === 'recibir') {
    if (monedaTengo === 'USD') texto = `Recibirás S/${(monto * sunat.venta).toFixed(2)} soles.`;
    else texto = `Recibirás $${(monto / sunat.compra).toFixed(2)} dólares.`;
  }
  // ======================
  // MODO: NECESITO
  // ======================
  else {
    if (monedaTengo === 'USD') texto = `Necesitas S/${(monto * sunat.compra).toFixed(2)} soles para recibir $${monto}.`;
    else texto = `Necesitas $${(monto / sunat.venta).toFixed(2)} dólares para recibir S/${monto}.`;
  }

  out.textContent = texto;
}

function syncAdornmentAndChips() {
  const selTengo = document.getElementById('moneda-tengo');
  const chips = document.querySelectorAll('.quick-amt');
  const adorn = document.querySelector('.input-with-icon .icon-left');

  const isPEN = selTengo?.value === 'PEN';
  if (adorn) adorn.textContent = isPEN ? 'S/' : '$';

  // valores de chips: solo cambian el prefijo visual
  chips.forEach(btn => {
    const v = btn.dataset.amt;
    btn.textContent = (isPEN ? 'S/ ' : '$ ') + Number(v).toLocaleString('es-PE');
  });
}
