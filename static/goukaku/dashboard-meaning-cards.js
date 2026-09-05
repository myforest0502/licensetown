document.addEventListener('DOMContentLoaded', () => {
  const phase = document.querySelector('.phase12-guidance-preview');
  const footer = document.querySelector('.dashboard-footer-cards');
  const weekly = window.LT_WEEKLY_LEARNING_SNAPSHOT || {};

  if (phase) {
    phase.classList.add('learning-position-card');

    const heading = phase.querySelector('.phase12-preview-heading h2');
    if (heading) heading.textContent = '🧭 学習の現在地';
    const badge = phase.querySelector('.phase12-preview-heading span');
    if (badge) badge.remove();

    const originalHeadline = phase.querySelector(':scope > strong');
    if (originalHeadline) {
      originalHeadline.textContent = 'いまは、間違いを直して理解を確かめる段階です';
      originalHeadline.classList.add('learning-position-headline');
    }

    const reason = phase.querySelector('.phase12-preview-reason');
    if (reason) {
      reason.insertAdjacentHTML(
        'afterend',
        '<p class="learning-position-help">ここでは「今日何問やるか」ではなく、学習履歴から見た現在の状態を表示しています。</p>'
      );
    }

    const action = phase.querySelector('.phase12-preview-action');
    if (action) action.remove();
    const actionStatus = phase.querySelector('.recommend-challenge-status');
    if (actionStatus) actionStatus.remove();
    const note = phase.querySelector('.phase12-preview-note');
    if (note) {
      note.textContent = '修復＝間違えた知識を、別の問題でもう一度確認して理解を確かめている状態です。';
    }

    const stateSummary = phase.querySelector('.phase12-state-summary');
    if (stateSummary && footer) {
      const stateCard = document.createElement('article');
      stateCard.className = 'motivation-card knowledge-state-card';
      stateCard.innerHTML = '<h2>🔧 知識の確認状況</h2><p class="knowledge-state-lead">LTが今どの知識を「確認・修復・定着」のどこまで見ているかです。</p>';
      stateCard.appendChild(stateSummary);
      stateCard.insertAdjacentHTML(
        'beforeend',
        '<dl class="knowledge-state-help">' +
          '<div><dt>確認中</dt><dd>まず理解できているかを見ている知識</dd></div>' +
          '<div><dt>修復中</dt><dd>誤答などがあり、別問題で確認している知識</dd></div>' +
          '<div><dt>修復済み</dt><dd>いったん理解し直せたことを確認できた知識</dd></div>' +
          '<div><dt>再確認待ち・定着</dt><dd>時間を空けて確認する知識／時間を空けても確認できた知識</dd></div>' +
        '</dl>'
      );
      footer.prepend(stateCard);
    }
  }

  if (!footer) return;

  footer.querySelectorAll('.reward-card, .target-progress-card').forEach((card) => card.remove());

  const days = Array.isArray(weekly.daily) ? weekly.daily : [];
  const learningDays = Math.max(Number(weekly.learningDays) || 0, 0);
  const answers = Math.max(Number(weekly.answers) || 0, 0);
  const correct = Math.max(Number(weekly.correct) || 0, 0);
  const incorrect = Math.max(answers - correct, 0);
  const accuracy = answers > 0 ? Math.round((correct / answers) * 100) : 0;
  const minutes = Math.max(Number(weekly.minutes) || 0, 0);

  const maxAnswers = Math.max(...days.map((item) => Number(item.answered_count) || 0), 1);
  const bars = days.map((item) => {
    const count = Math.max(Number(item.answered_count) || 0, 0);
    const height = count > 0 ? Math.max(Math.round((count / maxAnswers) * 52), 8) : 2;
    const label = String(item.label || '');
    return `<div class="weekly-spark-day"><span>${count}</span><i style="height:${height}px"></i><small>${label}</small></div>`;
  }).join('');

  const weeklyCard = document.createElement('article');
  weeklyCard.className = 'motivation-card weekly-learning-card';
  weeklyCard.innerHTML = `
    <h2>📊 今週の学習記録</h2>
    <p class="weekly-learning-lead">直近7日間の「どれだけ取り組んだか」を事実だけでまとめています。</p>
    <div class="weekly-learning-metrics">
      <div><span>学習した日</span><strong>${learningDays}<small>/7日</small></strong></div>
      <div><span>回答</span><strong>${answers}<small>問</small></strong></div>
      <div><span>正解 / 誤答</span><strong>${correct}<small> / ${incorrect}問</small></strong></div>
      <div><span>正答率</span><strong>${accuracy}<small>%</small></strong></div>
      <div><span>学習時間</span><strong>${Math.floor(minutes / 60)}<small>時間${minutes % 60}分</small></strong></div>
    </div>
    <div class="weekly-spark" aria-label="直近7日間の回答数">${bars}</div>
    <small class="weekly-learning-note">※「今日のおすすめ」や源さんの助言とは別に、1週間の量と波だけを振り返る欄です。</small>
  `;

  const footprint = footer.querySelector('.footprint-card');
  if (footprint) footer.insertBefore(weeklyCard, footprint);
  else footer.appendChild(weeklyCard);
});
