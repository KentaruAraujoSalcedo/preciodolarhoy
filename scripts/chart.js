// ==============================
// File: scripts/chart.js
// ==============================
import { state } from './state.js';

export function renderGraficoHistorico(ultimos7) {
  const canvas = document.getElementById('graficoSunat');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const labels  = ultimos7.map(d => d.fecha);
  const compras = ultimos7.map(d => d.compra);
  const ventas  = ultimos7.map(d => d.venta);

  // Destruye gráfico anterior si existe
  if (state.chart) state.chart.destroy();

  state.chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Compra SUNAT',
          data: compras,
          borderColor: '#16A34A',           // verde marca
          backgroundColor: 'rgba(22,163,74,.08)',
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.25
        },
        {
          label: 'Venta SUNAT',
          data: ventas,
          borderColor: '#2563EB',           // azul marca
          backgroundColor: 'rgba(37,99,235,.08)',
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.25
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,

      interaction: {
        intersect: false,
        mode: 'index'
      },

      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            font: { weight: 'bold' }
          }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const v = ctx.parsed.y;
              return `${ctx.dataset.label}: S/ ${v.toFixed(3)}`;
            }
          }
        }
      },

      scales: {
        x: {
          grid: { display: false }
        },
        y: {
          beginAtZero: false,
          ticks: {
            callback: (v) => `S/ ${v}`
          },
          grid: {
            color: 'rgba(0,0,0,.05)'
          }
        }
      }
    }
  });
}

// ✅ Wrapper: dibuja usando lo que ya tengas guardado en state
export function renderSunatChartFromState() {
  // intenta encontrar el histórico en donde lo guardes
  const hist =
    state.ultimos7 ||
    state.historicoSunat ||
    state.sunatHistorico ||
    state.sunatHistorico7 ||
    state.historico ||
    [];

  if (!Array.isArray(hist) || hist.length === 0) {
    console.warn('No hay histórico SUNAT en state para graficar.');
    return;
  }

  renderGraficoHistorico(hist);
}
