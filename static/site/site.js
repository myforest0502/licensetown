const menuButton = document.querySelector('.menu-button');
const nav = document.querySelector('.site-nav');

if (menuButton && nav) {
  menuButton.addEventListener('click', () => {
    const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!isOpen));
    nav.classList.toggle('is-open', !isOpen);
  });

  nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
    menuButton.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
  }));
}

const videoPlaceholder = document.querySelector('[data-video-placeholder]');
if (videoPlaceholder) {
  videoPlaceholder.addEventListener('click', () => {
    const status = videoPlaceholder.querySelector('small');
    if (status) status.textContent = 'デモ動画は準備中です';
  });
}
