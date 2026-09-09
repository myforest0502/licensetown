document.addEventListener('DOMContentLoaded', () => {
  const grid = document.querySelector('.dashboard-grid');
  const learnerNavigation = document.querySelector('.learner-navigation');
  const learningOverview = document.querySelector('.learning-overview');
  const subjectCard = document.querySelector('.subject-card');
  const guidanceStack = document.querySelector('.guidance-stack');
  const phaseGrid = document.querySelector('.phase-profile-grid');
  const phaseCard = document.querySelector('.learning-position-card');
  const profileCard = document.querySelector('.study-profile-card');
  const footer = document.querySelector('.dashboard-footer-cards');
  const weeklyCard = document.querySelector('.weekly-learning-card');

  if (!grid || !subjectCard || !guidanceStack) return;

  // The signed learner page already has a formal learner-navigation block built
  // from question_attempts -> derived Node state. When that block exists, do
  // not leave the legacy weakness/recommendation cards on screen as a second
  // competing decision authority.
  if (learnerNavigation) {
    const legacyWeakCard = guidanceStack.querySelector('.weak-card');
    const legacyRecommendCard = guidanceStack.querySelector('.recommend-card');
    if (legacyWeakCard) legacyWeakCard.remove();
    if (legacyRecommendCard) legacyRecommendCard.remove();

    // Until the backend formally enables field-progress presentation on this
    // route, the old subject rows are factual accuracy summaries only. Do not
    // label them as formal attainment.
    if (!subjectCard.querySelector('.field-progress-list')) {
      const subjectHeading = subjectCard.querySelector('.section-title h2');
      if (subjectHeading) subjectHeading.textContent = '分野別 正答率（参考）';
    }
  }

  const story = document.createElement('section');
  story.className = 'dashboard-story-layout';

  const left = document.createElement('div');
  left.className = 'dashboard-story-left';
  const right = document.createElement('div');
  right.className = 'dashboard-story-right';

  // Keep the long subject overview on the left, then deliberately move two
  // diagnostic cards from the right stack so both columns carry comparable
  // information density.  Do not create vertical spacer gaps just to align
  // the bottoms; cards should follow one another naturally.
  left.appendChild(subjectCard);

  const stateProgressCard = guidanceStack.querySelector('.state-progress-card');
  const strategyCard = guidanceStack.querySelector('.strategy-note-card');
  if (stateProgressCard) left.appendChild(stateProgressCard);
  if (strategyCard) left.appendChild(strategyCard);
  if (phaseCard) left.appendChild(phaseCard);

  right.appendChild(guidanceStack);
  if (profileCard) guidanceStack.appendChild(profileCard);

  story.append(left, right);

  if (learnerNavigation) {
    learnerNavigation.insertAdjacentElement('afterend', story);
  } else if (learningOverview) {
    learningOverview.parentNode.insertBefore(story, learningOverview);
  }

  if (learningOverview && !learningOverview.children.length) learningOverview.remove();
  if (phaseGrid && !phaseGrid.children.length) phaseGrid.remove();

  if (weeklyCard) {
    weeklyCard.classList.add('weekly-learning-card-full');
    story.insertAdjacentElement('afterend', weeklyCard);
  }

  if (footer) {
    footer.classList.add('dashboard-footer-compact');
    const leftStack = footer.querySelector('.dashboard-footer-left');
    if (leftStack) {
      Array.from(leftStack.children).forEach((card) => footer.appendChild(card));
      leftStack.remove();
    }
    if (weeklyCard && weeklyCard.parentNode === footer) weeklyCard.remove();
  }
});
