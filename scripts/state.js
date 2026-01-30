// ==============================
// File: scripts/state.js
// ==============================

// Estado global mínimo
// Centraliza datos + UI sin lógica pesada
export const state = {
  // ==========================
  // DATA
  // ==========================
  tasas: [],            // todas las casas (válidas + inválidas)
  validas: [],          // casas con compra/venta numéricas
  invalidas: [],        // casas con compra/venta inválidas

  mejorCompra: null,    // max compra global
  mejorVenta: null,     // min venta global

  winnerCompra: null,   // casa con mejor compra (CTA)
  winnerVenta: null,    // casa con mejor venta (CTA)

  sunat: {
    compra: null,
    venta: null
  },

  // ==========================
  // UI / INTERACCIÓN
  // ==========================
  modo: 'recibir',      // 'recibir' | 'necesito'
  monedaTengo: 'USD',   // 'USD' | 'PEN'
  monedaQuiero: 'PEN',  // siempre la opuesta
  monto: NaN,           // ✅ mejor: vacío = NaN (tu UI ya lo soporta)

  soloVerificadas: false, // filtro UI (futuro)
  ready: false,           // data lista

  // ==========================
  // RUNTIME
  // ==========================
  chart: null,          // instancia Chart.js
  meta: null,           // hora de carga de datos
  historico7: null      // ✅ cache del histórico (últimos 7)
};

// Patch simple (intencionalmente)
export const setState = (patch) => Object.assign(state, patch);

// Helpers
export const isReadySunat = () =>
  Number.isFinite(state.sunat.compra) &&
  Number.isFinite(state.sunat.venta);
