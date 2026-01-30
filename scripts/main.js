// ==============================
// File: scripts/main.js
// ==============================
import { state, setState } from './state.js';
import {
  cargarTasas,
  cargarSunatDesdeTasas,
  cargarHistorico,
  cargarMeta              // ✅ NUEVO
} from './data.js';

import {
  initStaticUI,
  bindEvents,
  renderTabla,
  renderSunat,
  renderResultadoConversor,
  renderBestDeal,
  syncMontoUI
} from './ui/index.js';

import { renderGraficoHistorico } from './chart.js';

window.addEventListener('DOMContentLoaded', init);

async function init() {
  try {
    // 1) UI estática (fallback)
    initStaticUI();

    // 2) Estado inicial desde DOM
    const modoIni =
      document.querySelector('input[name="modo"]:checked')?.value || 'recibir';

    const monedaTengoIni =
      document.getElementById('moneda-tengo')?.value || 'USD';

    const monedaQuieroIni =
      document.getElementById('moneda-quiero')?.value || 'PEN';

    const montoIniRaw = document.getElementById('monto')?.value ?? '';
    const montoIni = parseFloat(String(montoIniRaw).replace(',', '.'));

    setState({
      modo: modoIni,
      monedaTengo: monedaTengoIni,
      monedaQuiero: monedaQuieroIni,
      monto: Number.isFinite(montoIni) ? montoIni : NaN
    });

    // 3) Datos (tasas + SUNAT)
    await cargarTasas();
    await cargarSunatDesdeTasas();

    // ✅ 3.1) Meta real de scrapers (Actualizado REAL)
    const meta = await cargarMeta();
    pintarActualizado(meta);

    // 4) Header: mejores valores globales
    pintarMejoresHeader();

    // 5) Render inicial completo
    renderAll();

    // 6) Modal gráfico: cargar y dibujar SOLO cuando se abre
    const btnOpenChart = document.getElementById('btn-open-chart');

    btnOpenChart?.addEventListener('click', async () => {
      try {
        if (!state.historico7) {
          const ultimos7 = await cargarHistorico();
          setState({ historico7: ultimos7 });
        }

        renderGraficoHistorico(state.historico7);

        // cuando el modal ya está visible, forzar resize
        setTimeout(() => {
          state.chart?.resize?.();
        }, 0);
      } catch (e) {
        console.warn('Histórico no disponible:', e);
      }
    });

    // 7) Eventos reactivos
    bindEvents({
      onChange: () => {
        syncMontoUI();

        renderSunat();
        renderTabla();
        renderResultadoConversor();
        renderBestDeal();
        pintarMejoresHeader();
      },
    });
  } catch (e) {
    console.error('Error inicializando la app:', e);
  }
}

// ==================================================
// Render helpers
// ==================================================
function renderAll() {
  syncMontoUI();

  renderSunat();
  renderTabla();
  renderResultadoConversor();
  renderBestDeal();
}

function pintarMejoresHeader() {
  const bc = document.getElementById('best-compra');
  const bv = document.getElementById('best-venta');

  if (bc) {
    bc.textContent = Number.isFinite(state.mejorCompra)
      ? state.mejorCompra.toFixed(3)
      : '—';
  }

  if (bv) {
    bv.textContent = Number.isFinite(state.mejorVenta)
      ? state.mejorVenta.toFixed(3)
      : '—';
  }
}

// ✅ NUEVO: pinta "Actualizado" con la fecha REAL del scrape
function pintarActualizado(meta) {
  const fechaEl = document.getElementById('fecha');
  const horaEl = document.getElementById('hora');
  if (!fechaEl || !horaEl) return;

  // si no hay meta, deja el fallback que puso initStaticUI()
  if (!meta?.run_at_utc) return;

  const d = new Date(meta.run_at_utc);

  fechaEl.textContent = d.toLocaleDateString('es-PE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  horaEl.textContent = d.toLocaleTimeString('es-PE', {
    hour: '2-digit',
    minute: '2-digit',
  });
}
