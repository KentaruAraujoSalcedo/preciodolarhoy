// ==============================
// File: scripts/ui/index.js
// ==============================
import { initSunatModal } from './modal.js';

export { initStaticUI } from './static.js';
export { bindEvents } from './events.js';

export { renderTabla, recalcularCeldas } from './table.js';
export { renderSunat } from './sunat.js';
export { renderResultadoConversor, syncMontoUI } from './conversor.js';

// (Opcional) re-export para debug/logos
export { getCasaLogoSrc } from './logos.js';

export { renderBestDeal } from './bestDeal.js';