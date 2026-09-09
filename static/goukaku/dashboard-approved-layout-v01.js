document.addEventListener('DOMContentLoaded', () => {
  const grid = document.querySelector('.dashboard-grid');
  if (!grid) return;

  const dateCard = document.querySelector('.date-card');
  const overallCard = document.querySelector('.overall-progress-preview, .card.achievement');
  const routeCard = document.querySelector('.lt-exam-plan-card');
  const learnerNavigation = document.querySelector('.learner-navigation');
  const todayCard = document.querySelector('.learner-today-card');
  const summaryGrid = document.querySelector('.summary-grid');
  const story = document.querySelector('.dashboard-story-layout');
  const subjectCard = document.querySelector('.subject-card');
  const strategyCard = document.querySelector('.strategy-note-card');
  const phaseCard = document.querySelector('.learning-position-card');
  const gensanCard = document.querySelector('.gensan-card');
  const stateCard = document.querySelector('.knowledge-state-card');
  const profileCard = document.querySelector('.study-profile-card');
  const stateProgressCard = document.querySelector('.state-progress-card');
  const weeklyCard = document.querySelector('.weekly-learning-card');
  const footprintCard = document.querySelector('.footprint-card');
  const nextCheckCard = document.querySelector('.next-check-card');
  const oldTopStack = document.querySelector('.lt-top-left-stack');
  const guidanceStack = document.querySelector('.guidance-stack');
  const footer = document.querySelector('.dashboard-footer-cards');

  // Boss-approved layout. Do not reinterpret the order.
  // UPPER HALF (current reference image):
  //   left = date -> today's study; right = overall progress spanning that height
  //   then summary -> recommended route -> learner decision/navigation.
  // LOWER HALF (previously approved reference image): unchanged.
  let top = document.querySelector('.dashboard-reference-top');
  if (!top) {
    top = document.createElement('section');
    top.className = 'dashboard-reference-top';
    const firstContent = Array.from(grid.children).find((el) =>
      !el.classList.contains('learner-preview-banner') && !el.classList.contains('readonly-banner')
    );
    if (firstContent) grid.insertBefore(top, firstContent);
    else grid.appendChild(top);
  }

  const move = (parent, child) => {
    if (parent && child && child.parentElement !== parent) parent.appendChild(child);
  };

  // Pull top-level cards out of legacy wrappers before placing them once.
  [dateCard, overallCard, routeCard, learnerNavigation, summaryGrid, story].forEach((el) => {
    if (el && el.parentElement && el.parentElement !== grid && el.parentElement !== top) grid.appendChild(el);
  });
  if (oldTopStack && !oldTopStack.children.length) oldTopStack.remove();

  const topSplit = document.createElement('div');
  topSplit.className = 'dashboard-reference-top-split';
  const topLeft = document.createElement('div');
  topLeft.className = 'dashboard-reference-top-left';
  const topRight = document.createElement('div');
  topRight.className = 'dashboard-reference-top-right';
  topSplit.append(topLeft, topRight);
  top.appendChild(topSplit);

  // Exact upper-half placement from the latest reference.
  move(topLeft, dateCard);
  move(topLeft, todayCard);
  move(topRight, overallCard);
  move(top, summaryGrid);
  move(top, routeCard);
  move(top, learnerNavigation);

  // LOWER HALF: frozen to the previously approved reference image. Do not alter this placement.
  let lower = document.querySelector('.dashboard-reference-lower');
  if (!lower) {
    lower = document.createElement('section');
    lower.className = 'dashboard-reference-lower';
    top.insertAdjacentElement('afterend', lower);
  }

  [subjectCard, gensanCard, stateCard, profileCard, stateProgressCard, strategyCard, weeklyCard, phaseCard, footprintCard, nextCheckCard]
    .filter(Boolean)
    .forEach((card) => lower.appendChild(card));

  // Legacy containers are no longer layout authorities once their cards have been moved.
  if (story && !story.children.length) story.remove();
  if (guidanceStack && !guidanceStack.children.length) guidanceStack.remove();
  if (footer && !footer.children.length) footer.remove();

  // Always use the established production Gen-san asset; mockup/generated faces are never used.
  const gensanImage = gensanCard?.querySelector('img');
  if (gensanImage) gensanImage.src = '/static/images/characters/gensan_main.png';

  grid.classList.add('dashboard-reference-layout');
});
