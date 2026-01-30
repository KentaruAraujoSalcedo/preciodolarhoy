// ==============================
// File: scripts/ui/format.js
// ==============================

export const moneyFmt = (n, cur) =>
  Number.isFinite(n)
    ? n.toLocaleString('es-PE', { style: 'currency', currency: cur })
    : '-';

export const rateFmt = (n) =>
  Number.isFinite(n) ? n.toFixed(3) : '–';