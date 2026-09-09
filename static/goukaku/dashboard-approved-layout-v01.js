document.addEventListener('DOMContentLoaded', () => {
  const grid = document.querySelector('.dashboard-grid');
  if (!grid) return;

  const dateCard = document.querySelector('.date-card');
  const overallCard = document.querySelector('.overall-progress-preview, .card.achievement');
  const routeCard = document.querySelector('.lt-exam-plan-card');
  const learnerNavigation = document.querySelector('.learner-navigation');
  const summaryGrid = document.querySelector('.summary-grid');
  const story = document.querySelector('.dashboard-story-layout');
  const left = story?.querySelector('.dashboard-story-left');
  const right = story?.querySelector('.dashboard-story-right');
  const guidanceStack = document.querySelector('.guidance-stack');
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
  const footer = document.querySelector('.dashboard-footer-cards');
  const oldTopStack = document.querySelector('.lt-top-left-stack');

  // Approved production hierarchy:
  // top facts -> large recommended route -> today's action -> facts -> two balanced columns.
  // Pull the date and route out of the old left-only wrapper first.
  if (dateCard && dateCard.parentElement !== grid) grid.appendChild(dateCard);
  if (routeCard && routeCard.parentElement !== grid) grid.appendChild(routeCard);
  if (oldTopStack && !oldTopStack.children.length) oldTopStack.remove();

  if (dateCard) grid.prepend(dateCard);
  if (overallCard && overallCard !== dateCard) dateCard?.insertAdjacentElement('afterend', overallCard);
  if (routeCard) overallCard?.insertAdjacentElement('afterend', routeCard);
  if (learnerNavigation) routeCard?.insertAdjacentElement('afterend', learnerNavigation);
  if (summaryGrid) learnerNavigation?.insertAdjacentElement('afterend', summaryGrid);
  if (story) summaryGrid?.insertAdjacentElement('afterend', story);

  if (left && right && guidanceStack) {
    // Left rail: field view -> strategy -> current position -> footprints.
    if (subjectCard) left.appendChild(subjectCard);
    if (strategyCard) left.appendChild(strategyCard);
    if (phaseCard) left.appendChild(phaseCard);
    if (footprintCard) left.appendChild(footprintCard);

    // Right rail: Gen-san -> knowledge -> chart -> retention -> weekly -> checkpoint.
    if (gensanCard) guidanceStack.appendChild(gensanCard);
    if (stateCard) guidanceStack.appendChild(stateCard);
    if (profileCard) guidanceStack.appendChild(profileCard);
    if (stateProgressCard) guidanceStack.appendChild(stateProgressCard);
    if (weeklyCard) guidanceStack.appendChild(weeklyCard);
    if (nextCheckCard) guidanceStack.appendChild(nextCheckCard);
    right.appendChild(guidanceStack);
  }

  // The formal Gen-san asset is already the production source of truth.
  // Reassert it here so layout/mockup work can never replace the real character.
  const gensanImage = gensanCard?.querySelector('img');
  if (gensanImage) gensanImage.src = '/static/images/characters/gensan_main.png';

  if (footer) {
    Array.from(footer.children).forEach((child) => {
      if (child.classList?.contains('footprint-card') && left) left.appendChild(child);
      else if (child.classList?.contains('next-check-card') && guidanceStack) guidanceStack.appendChild(child);
    });
    if (!footer.children.length) footer.remove();
  }

  grid.classList.add('dashboard-approved-layout');
});
