document.addEventListener('DOMContentLoaded', () => {
  const dashboardGrid = document.querySelector('.dashboard-grid');
  const learnerNavigation = document.querySelector('.learner-navigation');
  const summaryGrid = document.querySelector('.summary-grid');
  const phase = document.querySelector('.phase12-guidance-preview');
  const footer = document.querySelector('.dashboard-footer-cards');
  const guidanceStack = document.querySelector('.guidance-stack');
  const learnerDetails = document.querySelector('.learner-nav-detail-grid');
  const currentCard = document.querySelector('.learner-current-card');
  const attentionCard = document.querySelector('.learner-attention-card');
  const todayCard = document.querySelector('.learner-today-card');
  const weekly = window.LT_WEEKLY_LEARNING_SNAPSHOT || {};
  let stateCard = null;
  let stateProgressCard = null;
  let strategyCard = null;

  // Paid-product hierarchy: deadline/progress first, then the LT decision/navigation.
  if (dashboardGrid && learnerNavigation && summaryGrid) {
    summaryGrid.insertAdjacentElement('afterend', learnerNavigation);
  }

  const detailSections = learnerDetails
    ? Array.from(learnerDetails.querySelectorAll(':scope > section'))
    : [];

  const cloneFirstDetail = (section, title) => {
    if (!section) return null;
    const article = document.createElement('article');
    const heading = document.createElement('h3');
    heading.textContent = title;
    article.appendChild(heading);
    const first = section.querySelector('p');
    if (first) article.appendChild(first.cloneNode(true));
    return article;
  };

  if (currentCard && detailSections.length) {
    const detailGrid = document.createElement('div');
    detailGrid.className = 'learner-current-detail-grid';
    [
      cloneFirstDetail(detailSections[0], '安定していること'),
      cloneFirstDetail(detailSections[1], 'いま修復していること'),
      cloneFirstDetail(detailSections[2], 'まだ確認したいこと'),
    ].filter(Boolean).forEach((item) => detailGrid.appendChild(item));
    if (detailGrid.children.length) currentCard.appendChild(detailGrid);
  }

  if (todayCard) {
    const topPriority = attentionCard?.querySelector('.learner-attention-list > div:first-child');
    const field = topPriority?.querySelector('b')?.textContent?.trim() || '学習データから選定';
    const status = topPriority?.querySelector('span')?.textContent?.trim() || '優先して確認';
    const amount = todayCard.querySelector('h2')?.textContent?.trim() || '今日のおすすめ';
    const summary = document.createElement('div');
    summary.className = 'learner-today-summary';
    [
      ['優先分野', field],
      ['今の状態', status],
      ['今日の学習量', amount],
    ].forEach(([label, value]) => {
      const box = document.createElement('div');
      const span = document.createElement('span');
      const strong = document.createElement('strong');
      span.textContent = label;
      strong.textContent = value;
      box.append(span, strong);
      summary.appendChild(box);
    });
    todayCard.appendChild(summary);
  }

  if (phase) {
    phase.classList.add('learning-position-card');

    const heading = phase.querySelector('.phase12-preview-heading h2');
    if (heading) heading.textContent = '🧭 学習の現在地';
    const badge = phase.querySelector('.phase12-preview-heading span');
    if (badge) badge.remove();

    const originalHeadline = phase.querySelector(':scope > strong');
    if (originalHeadline) originalHeadline.classList.add('learning-position-headline');

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
    if (stateSummary) {
      stateCard = document.createElement('article');
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

      const values = Array.from(stateSummary.querySelectorAll('div')).map((item) => ({
        label: item.querySelector('dt')?.textContent?.trim() || '',
        value: Number((item.querySelector('dd')?.textContent || '').replace(/[^0-9]/g, '')) || 0,
      }));
      const byLabel = (name) => values.find((item) => item.label.includes(name))?.value || 0;
      const repairing = byLabel('修復中');
      const repaired = byLabel('修復済み');
      const recheck = byLabel('再確認待ち');
      const stable = byLabel('定着');

      stateProgressCard = document.createElement('article');
      stateProgressCard.className = 'motivation-card state-progress-card';
      stateProgressCard.innerHTML = `
        <h2>🪜 定着までの進み方</h2>
        <p>「解けた」で終わらず、直す → 時間を空ける → もう一度確認する、までをLTが追います。</p>
        <div class="state-progress-flow">
          <div><span>1</span><b>修復中</b><strong>${repairing}</strong><small>別問題で理解を確認</small></div>
          <i>→</i>
          <div><span>2</span><b>修復済み</b><strong>${repaired}</strong><small>いったん理解を確認</small></div>
          <i>→</i>
          <div><span>3</span><b>再確認待ち</b><strong>${recheck}</strong><small>時間を空けて再確認</small></div>
          <i>→</i>
          <div><span>4</span><b>定着</b><strong>${stable}</strong><small>時間を空けても確認</small></div>
        </div>`;
    }

    const positionMain = document.createElement('div');
    positionMain.className = 'learning-position-main';
    Array.from(phase.childNodes).forEach((node) => positionMain.appendChild(node));
    const positionAside = document.createElement('aside');
    positionAside.className = 'learning-position-aside';
    const retentionText = detailSections[3]?.textContent?.replace(/\s+/g, ' ').trim() || '修復した知識は、時間を空けてもう一度確認します。';
    positionAside.innerHTML = `
      <h3>ここから次の段階へ</h3>
      <div><b>① 直す</b><span>自信を持って間違えた内容を、別問題で確認</span></div>
      <div><b>② 時間を空ける</b><span>その場で覚えただけではないかを見る</span></div>
      <div><b>③ 定着を確かめる</b><span>時間を空けても答えられたら「定着」へ</span></div>
      <p>${retentionText}</p>`;
    phase.append(positionMain, positionAside);
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

  const formatPeriodLabel = (label) => {
    const parts = String(label || '').split('/');
    if (parts.length !== 2) return String(label || '');
    const month = Number(parts[0]);
    const day = Number(parts[1]);
    if (!Number.isFinite(month) || !Number.isFinite(day)) return String(label || '');
    return `${month}月${day}日`;
  };
  const periodText = days.length
    ? `${formatPeriodLabel(days[0].label)}〜${formatPeriodLabel(days[days.length - 1].label)}`
    : '';

  const maxAnswers = Math.max(...days.map((item) => Number(item.answered_count) || 0), 1);
  const bars = days.map((item) => {
    const count = Math.max(Number(item.answered_count) || 0, 0);
    const height = count > 0 ? Math.max(Math.round((count / maxAnswers) * 92), 10) : 2;
    const label = String(item.label || '');
    return `<div class="weekly-spark-day"><span>${count}</span><i style="height:${height}px"></i><small>${label}</small></div>`;
  }).join('');
  const avgPerLearningDay = learningDays ? Math.round(answers / learningDays) : 0;
  const strongestDay = days.reduce((best, item) => (Number(item.answered_count) || 0) > (Number(best.answered_count) || 0) ? item : best, days[0] || {});

  const weeklyCard = document.createElement('article');
  weeklyCard.className = 'motivation-card weekly-learning-card';
  weeklyCard.innerHTML = `
    <div class="weekly-learning-heading">
      <div><h2>📊 直近7日間の学習記録</h2><p class="weekly-learning-lead">「どれだけ取り組んだか」を事実だけでまとめています。</p></div>
      ${periodText ? `<strong class="weekly-period">${periodText}</strong>` : ''}
    </div>
    <div class="weekly-learning-metrics">
      <div><span>学習した日</span><strong>${learningDays}<small>/7日</small></strong></div>
      <div><span>回答</span><strong>${answers}<small>問</small></strong></div>
      <div><span>正解 / 誤答</span><strong>${correct}<small> / ${incorrect}問</small></strong></div>
      <div><span>正答率</span><strong>${accuracy}<small>%</small></strong></div>
      <div><span>学習時間</span><strong>${Math.floor(minutes / 60)}<small>時間${minutes % 60}分</small></strong></div>
    </div>
    <div class="weekly-spark" aria-label="直近7日間の回答数">${bars}</div>
    <div class="weekly-learning-detail">
      <div><span>学習した日の平均</span><strong>${avgPerLearningDay}問/日</strong></div>
      <div><span>最も取り組んだ日</span><strong>${strongestDay.label || '--'}　${Number(strongestDay.answered_count) || 0}問</strong></div>
      <div><span>7日間の見方</span><strong>量だけでなく、継続と修復の進み方を一緒に見ます</strong></div>
    </div>`;

  let profileCard = null;
  let nextCheckCard = null;
  if (learnerDetails) {
    const grid = learnerDetails.cloneNode(true);
    grid.classList.add('study-profile-grid');
    const sections = Array.from(grid.querySelectorAll(':scope > section'));

    if (sections[3]) {
      nextCheckCard = document.createElement('article');
      nextCheckCard.className = 'motivation-card next-check-card';
      const nextBody = sections[3].cloneNode(true);
      const nextHeading = nextBody.querySelector('h3');
      if (nextHeading) nextHeading.textContent = '次に確認すること';
      nextCheckCard.innerHTML = '<div class="next-check-heading"><h2>⏱ 次のチェックポイント</h2><p>忘れていないか、次にLTが確認する内容です。</p></div>';
      nextCheckCard.appendChild(nextBody);
      sections[3].remove();
    }

    profileCard = document.createElement('article');
    profileCard.className = 'motivation-card study-profile-card';
    profileCard.innerHTML = '<div class="study-profile-heading"><h2>🗂 今の学習カルテ</h2><p>「できている・直している・まだ確認できていない」を並べて確認します。</p></div>';
    const headings = ['安定していること', '修復中', 'まだ確認できていないこと'];
    grid.querySelectorAll(':scope > section').forEach((section, index) => {
      const h3 = section.querySelector('h3');
      if (h3 && headings[index]) h3.textContent = headings[index];
    });
    profileCard.appendChild(grid);
    const originalDetails = learnerDetails.closest('.learner-nav-details');
    if (originalDetails) originalDetails.classList.add('learner-nav-details-duplicated');
  }

  if (guidanceStack) {
    if (stateCard) guidanceStack.appendChild(stateCard);
    if (stateProgressCard) guidanceStack.appendChild(stateProgressCard);
    strategyCard = document.createElement('article');
    strategyCard.className = 'motivation-card strategy-note-card';
    const topItems = Array.from(attentionCard?.querySelectorAll('.learner-attention-list > div') || []).slice(0, 3);
    strategyCard.innerHTML = '<h2>📝 LTの作戦メモ</h2><p>今の学習履歴から、優先順位をこう見ています。</p><div class="strategy-note-list"></div>';
    const list = strategyCard.querySelector('.strategy-note-list');
    topItems.forEach((item, index) => {
      const field = item.querySelector('b')?.textContent?.trim() || '確認項目';
      const message = item.querySelector('p')?.textContent?.trim() || '優先して確認します。';
      list.insertAdjacentHTML('beforeend', `<div><span>${index + 1}</span><b>${field}</b><small>${message}</small></div>`);
    });
    if (!topItems.length) list.innerHTML = '<div><span>1</span><b>学習データを蓄積中</b><small>記録が増えると、優先順位がより具体的になります。</small></div>';
    guidanceStack.appendChild(strategyCard);
  } else {
    if (stateCard) footer.prepend(stateCard);
    if (stateProgressCard) footer.prepend(stateProgressCard);
  }

  if (phase) {
    const phaseProfileGrid = document.createElement('section');
    phaseProfileGrid.className = 'phase-profile-grid';
    phase.parentNode.insertBefore(phaseProfileGrid, phase);
    phaseProfileGrid.appendChild(phase);
    if (profileCard) phaseProfileGrid.appendChild(profileCard);
  } else if (profileCard) {
    footer.prepend(profileCard);
  }

  const footprint = footer.querySelector('.footprint-card');
  if (footprint) {
    footprint.classList.add('footprint-card-expanded');
    const textBlock = footprint.querySelector('div');
    if (textBlock) {
      textBlock.insertAdjacentHTML(
        'beforeend',
        '<div class="footprint-highlights"><span>学習した日</span><span>取り組んだ問題</span><span>成長の節目</span></div>'
      );
    }
  }

  footer.classList.add('dashboard-footer-split');
  const footerLeft = document.createElement('div');
  footerLeft.className = 'dashboard-footer-left';
  if (footprint) footerLeft.appendChild(footprint);
  if (nextCheckCard) footerLeft.appendChild(nextCheckCard);
  if (footerLeft.children.length) footer.appendChild(footerLeft);
  footer.appendChild(weeklyCard);
});