document.addEventListener('DOMContentLoaded', () => {
  const grid = document.querySelector('.dashboard-grid');
  if (!grid) return;

  const dateCard = document.querySelector('.date-card');
  const overallCard = document.querySelector('.overall-progress-preview, .card.achievement');
  const routeCard = document.querySelector('.lt-exam-plan-card');
  const learnerNavigation = document.querySelector('.learner-navigation');
  const attentionCard = document.querySelector('.learner-attention-card');
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

  // Rebuild the page to match the two reference screenshots exactly in hierarchy:
  // TOP: date + priority / overall progress -> summary -> learner decision -> recommended route.
  // BOTTOM: subject progress opposite four guidance cards, then strategy + current position
  // opposite the weekly record, finishing with footprints + next checkpoint.
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

  // Pull cards out of legacy wrappers before re-placing them.
  [dateCard, overallCard, routeCard, learnerNavigation, summaryGrid, story].forEach((el) => {
    if (el && el.parentElement && el.parentElement !== grid && el.parentElement !== top) grid.appendChild(el);
  });
  if (attentionCard && attentionCard.parentElement === learnerNavigation) learnerNavigation.removeChild(attentionCard);
  if (oldTopStack && !oldTopStack.children.length) oldTopStack.remove();

  // Top half from reference image 1.
  const topSplit = document.createElement('div');
  topSplit.className = 'dashboard-reference-top-split';
  const topLeft = document.createElement('div');
  topLeft.className = 'dashboard-reference-top-left';
  const topRight = document.createElement('div');
  topRight.className = 'dashboard-reference-top-right';
  topSplit.append(topLeft, topRight);
  top.appendChild(topSplit);

  move(topLeft, dateCard);
  move(topLeft, attentionCard);
  move(topRight, overallCard);
  move(top, summaryGrid);
  move(top, learnerNavigation);
  move(top, routeCard);

  // Lower half from reference image 2. Use one explicit grid so row alignment is deterministic.
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
