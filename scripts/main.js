// ==============================
// File: scripts/main.js
// ==============================
import { state, setState } from './state.js';
import { cargarTasas, cargarSunatDesdeTasas, cargarHistorico } from './data.js';
import { initStaticUI, bindEvents, renderTabla, renderSunat, renderResultadoConversor } from './ui.js';
import { renderGraficoHistorico } from './chart.js';

window.addEventListener('DOMContentLoaded', init);

async function init() {
  try {
    initStaticUI();

    // Estado inicial desde DOM
    const modoIni = document.querySelector('input[name="modo"]:checked')?.value || 'recibir';
    const monedaTengoIni = document.getElementById('moneda-tengo')?.value || 'USD';
    const monedaQuieroIni = document.getElementById('moneda-quiero')?.value || 'PEN';

    setState({ modo: modoIni, monedaTengo: monedaTengoIni, monedaQuiero: monedaQuieroIni });

    await cargarTasas();
    await cargarSunatDesdeTasas();

    // ⬇️ Nuevo: pinta mejores en el header
    const bc = document.getElementById('best-compra');
    const bv = document.getElementById('best-venta');
    if (bc) bc.textContent = Number.isFinite(state.mejorCompra) ? state.mejorCompra.toFixed(3) : '—';
    if (bv) bv.textContent = Number.isFinite(state.mejorVenta)  ? state.mejorVenta.toFixed(3)  : '—';

    renderSunat();
    renderTabla();
    renderResultadoConversor();

    // Gráfico histórico
    try {
      const ultimos7 = await cargarHistorico();
      renderGraficoHistorico(ultimos7);
    } catch (e) {
      console.warn('No se pudo cargar el histórico:', e);
    }

    // Eventos reactivos
    bindEvents({ onChange: () => {
      renderResultadoConversor();
      renderTabla(); // reordena según modo/monedas y recalcula celdas
    }});

  } catch (e) {
    console.error('Error inicializando la app:', e);
  }
}
