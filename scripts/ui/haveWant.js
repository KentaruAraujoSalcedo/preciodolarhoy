// ==============================
// File: scripts/ui/haveWant.js
// ==============================

import { state } from '../state.js';

// En recibir: (tengo -> quiero)
// En necesito: (quiero -> tengo)  ← se invierte
export function getHaveWant() {
  const { modo, monedaTengo, monedaQuiero } = state;

  const have = (modo === 'recibir') ? monedaTengo : monedaQuiero;
  const want = (modo === 'recibir') ? monedaQuiero : monedaTengo;

  return { have, want };
}