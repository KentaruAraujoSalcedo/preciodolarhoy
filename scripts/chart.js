// ==============================
// File: scripts/chart.js
// ==============================
import { state } from './state.js';

export function renderGraficoHistorico(ultimos7) {
  const canvas = document.getElementById('graficoSunat');
  if (!canvas) return; 
  const ctx = canvas.getContext('2d');

  const labels = ultimos7.map(d => d.fecha);
  const compras = ultimos7.map(d => d.compra);
  const ventas = ultimos7.map(d => d.venta);

  // Destruye gráfico anterior si existe
  if (state.chart) { state.chart.destroy(); }

  state.chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Compra (S/)', data: compras, fill: false },
        { label: 'Venta (S/)',  data: ventas,  fill: false }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: false } },
      interaction: { intersect: false, mode: 'index' },
      elements: { line: { tension: 0.2 } }
    }
  });
}