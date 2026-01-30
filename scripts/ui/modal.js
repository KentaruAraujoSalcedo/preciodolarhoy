// ==============================
// File: scripts/ui/modal.js
// ==============================

export function initSunatModal() {
  const modal = document.getElementById('chartModal');
  const openBtn = document.getElementById('btn-open-chart');
  if (!modal || !openBtn) return;

  const overlay = modal.querySelector('.modal__overlay');
  const closeBtn = modal.querySelector('.modal__close');

  function openModal() {
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
  }

  function closeModal() {
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
  }

  openBtn.addEventListener('click', openModal);
  closeBtn?.addEventListener('click', closeModal);
  overlay?.addEventListener('click', closeModal);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.getAttribute('aria-hidden') === 'false') {
      closeModal();
    }
  });
}
