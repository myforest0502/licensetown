document.addEventListener('DOMContentLoaded', () => {
  const target = document.querySelector('.recommend-card .daily-target');
  const summary = window.LT_RECOMMENDATION_DAILY_SUMMARY;
  if (!target || !summary) return;

  const goal = Number(summary.goal) || 0;
  const answered = Math.max(Number(summary.answered) || 0, 0);
  const correct = Math.max(Number(summary.correct) || 0, 0);
  const incorrect = Math.max(answered - correct, 0);
  if (goal <= 0) return;

  const achieved = answered >= goal;
  const remaining = Math.max(goal - answered, 0);
  const status = achieved ? '達成！' : `未達（あと${remaining}問）`;

  target.classList.add('lt-daily-summary');
  target.setAttribute(
    'aria-label',
    `今日の目標${goal}問：${status}。正解${correct}問、誤答${incorrect}問`
  );
  target.innerHTML =
    `今日の目標${goal}問：<strong>${status}</strong><br>` +
    `正解：${correct}問　誤答：${incorrect}問`;
});
