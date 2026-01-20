// ==============================
// File: scripts/state.js
// ==============================
// Estado global mínimo, centraliza valores compartidos
export const state = {
  tasas: [],           // todas las casas (válidas + inválidas)
  validas: [],         // casas con compra/venta numéricas
  invalidas: [],       // casas con compra/venta inválidas
  mejorCompra: null,   // max compra
  mejorVenta: null,    // min venta
  sunat: { compra: null, venta: null },

  // UI/Modo
  modo: 'recibir',                 // 'recibir' | 'necesito'
  monedaTengo: 'USD',              // 'USD' | 'PEN'
  monedaQuiero: 'PEN',             // siempre la opuesta
  monto: 0,                        // número

  chart: null                      // instancia Chart.js
};

export const setState = (patch) => Object.assign(state, patch);

export const isReadySunat = () => Number.isFinite(state.sunat.compra) && Number.isFinite(state.sunat.venta);
