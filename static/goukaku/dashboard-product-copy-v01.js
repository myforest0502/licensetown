document.addEventListener('DOMContentLoaded', () => {
  const currentCard = document.querySelector('.learner-current-card');
  const attentionCard = document.querySelector('.learner-attention-card');
  const todayCard = document.querySelector('.learner-today-card');
  const overallCard = document.querySelector('.overall-progress-preview');
  const weeklyCard = document.querySelector('.weekly-learning-card');
  const dateCard = document.querySelector('.date-card');

  const text = (el) => (el?.textContent || '').replace(/\s+/g, ' ').trim();
  const firstPriority = attentionCard?.querySelector('.learner-attention-list > div:first-child');
  const priorityField = text(firstPriority?.querySelector('b')) || '今の優先分野';
  const priorityLabel = text(firstPriority?.querySelector('span')) || '優先して確認';
  const priorityMessage = text(firstPriority?.querySelector('p')) || '学習履歴から、今いちばん効果が高い内容を優先します。';
  const todayAmount = text(todayCard?.querySelector('h2')) || '今日のおすすめ学習';
  const todayReason = text(todayCard?.querySelector('p')) || '今日の学習履歴に合わせて内容を選びます。';
  const currentHeadline = text(currentCard?.querySelector('h2')) || '現在地を確認中';

  const progressPoints = Array.isArray(window.LT_WEEKLY_LEARNING_SNAPSHOT?.overallProgress)
    ? window.LT_WEEKLY_LEARNING_SNAPSHOT.overallProgress : [];
  const firstProgress = Number(progressPoints[0]?.progress);
  const lastProgress = Number(progressPoints[progressPoints.length - 1]?.progress);
  const progressDelta = Number.isFinite(firstProgress) && Number.isFinite(lastProgress)
    ? Math.round((lastProgress - firstProgress) * 10) / 10 : null;

  const routeSnapshot = window.LT_ROUTE_SNAPSHOT || {};
  const countdownFromSnapshot = Number(routeSnapshot.daysUntilExam);
  const countdownFromCard = Number((text(dateCard?.querySelector('.countdown strong')) || '').replace(/[^0-9]/g, ''));
  const countdownNumber = Number.isFinite(countdownFromSnapshot) && countdownFromSnapshot >= 0
    ? countdownFromSnapshot : countdownFromCard;
  const totalAnswers = Number(routeSnapshot.totalAnswers) || 0;
  const uniqueAnsweredQuestions = Number(routeSnapshot.uniqueAnsweredQuestions) || 0;
  const currentProgress = Number.parseFloat((text(overallCard?.querySelector('.ring span')) || '').replace('%', ''));

  // LT推奨ペース v0.1。合格確率ではなく、試験日から逆算した学習到達指標の目安。
  // 日数が減るほど、新規範囲中心から修復・再確認・定着中心へ移る想定で段階的に加速させる。
  const ROUTE_ANCHORS = [
    { days: 365, progress: 0 },
    { days: 240, progress: 2 },
    { days: 180, progress: 5 },
    { days: 150, progress: 15 },
    { days: 120, progress: 30 },
    { days: 90, progress: 50 },
    { days: 60, progress: 70 },
    { days: 30, progress: 88 },
    { days: 14, progress: 96 },
    { days: 0, progress: 100 },
  ];

  const interpolateRecommendedProgress = (daysRemaining) => {
    if (!Number.isFinite(daysRemaining)) return null;
    if (daysRemaining >= ROUTE_ANCHORS[0].days) return ROUTE_ANCHORS[0].progress;
    if (daysRemaining <= 0) return 100;
    for (let i = 0; i < ROUTE_ANCHORS.length - 1; i += 1) {
      const start = ROUTE_ANCHORS[i];
      const end = ROUTE_ANCHORS[i + 1];
      if (daysRemaining <= start.days && daysRemaining >= end.days) {
        const ratio = (start.days - daysRemaining) / (start.days - end.days);
        return start.progress + ((end.progress - start.progress) * ratio);
      }
    }
    return null;
  };

  const equivalentDaysRemaining = (progress) => {
    if (!Number.isFinite(progress)) return null;
    const value = Math.max(0, Math.min(100, progress));
    if (value <= ROUTE_ANCHORS[0].progress) return ROUTE_ANCHORS[0].days;
    if (value >= 100) return 0;
    for (let i = 0; i < ROUTE_ANCHORS.length - 1; i += 1) {
      const start = ROUTE_ANCHORS[i];
      const end = ROUTE_ANCHORS[i + 1];
      if (value >= start.progress && value <= end.progress) {
        const width = end.progress - start.progress;
        const ratio = width > 0 ? (value - start.progress) / width : 0;
        return start.days - ((start.days - end.days) * ratio);
      }
    }
    return null;
  };

  const recommendedProgress = interpolateRecommendedProgress(countdownNumber);
  const equivalentDays = equivalentDaysRemaining(currentProgress);
  const scheduleDeltaDays = Number.isFinite(countdownNumber) && Number.isFinite(equivalentDays)
    ? Math.round(countdownNumber - equivalentDays) : null;
  const progressGap = Number.isFinite(currentProgress) && Number.isFinite(recommendedProgress)
    ? Math.round((currentProgress - recommendedProgress) * 10) / 10 : null;

  let scheduleLabel = '推奨ペースを計算中';
  let scheduleDetail = '学習データが増えると、推奨ラインとの差を確認できます。';
  if (scheduleDeltaDays !== null) {
    if (Math.abs(scheduleDeltaDays) <= 2) {
      scheduleLabel = 'ほぼ予定どおり';
      scheduleDetail = scheduleDeltaDays > 0 ? `約${scheduleDeltaDays}日先行` : scheduleDeltaDays < 0 ? `約${Math.abs(scheduleDeltaDays)}日遅れ` : '予定どおり';
    } else if (scheduleDeltaDays > 0) {
      scheduleLabel = scheduleDeltaDays <= 7 ? '推奨ペース内' : '前倒しで進行';
      scheduleDetail = `約${scheduleDeltaDays}日先行`;
    } else {
      scheduleLabel = scheduleDeltaDays >= -7 ? '推奨ペース内' : '少し巻き返したい';
      scheduleDetail = `約${Math.abs(scheduleDeltaDays)}日遅れ`;
    }
  }

  let weeklyLabel = '進み方を確認中';
  let weeklyCopy = '学習履歴が増えるほど、推奨ルートとのズレを細かく確認できるようになります。';
  if (progressDelta !== null && progressDelta > 0.2) {
    weeklyLabel = '今週は前進中';
    weeklyCopy = `直近7日間で到達度が ${progressDelta.toFixed(1)}pt 上がっています。今の優先分野を続けながら、修復した知識を再確認へつなげます。`;
  } else if (progressDelta !== null && progressDelta >= -0.2) {
    weeklyLabel = '今週は足場固め';
    weeklyCopy = '到達度は大きく動いていません。問題数だけを増やさず、修復と再確認を進める時期です。';
  } else if (progressDelta !== null) {
    weeklyLabel = '再確認フェーズ';
    weeklyCopy = '到達度が一時的に下がっています。覚えたままかを厳しく見直している可能性があります。';
  }

  if (dateCard && overallCard && currentCard && todayCard && !document.querySelector('.lt-top-left-stack')) {
    const stack = document.createElement('section');
    stack.className = 'lt-top-left-stack';
    dateCard.parentNode.insertBefore(stack, dateCard);
    stack.appendChild(dateCard);

    const recommendedDisplay = Number.isFinite(recommendedProgress) ? `${recommendedProgress.toFixed(1)}%` : '--';
    const currentDisplay = Number.isFinite(currentProgress) ? `${currentProgress.toFixed(1)}%` : '--';
    const gapDisplay = progressGap === null ? '--' : `${progressGap >= 0 ? '+' : ''}${progressGap.toFixed(1)}pt`;
    const activityCopy = totalAnswers > 0
      ? `${totalAnswers.toLocaleString('ja-JP')}回答・${uniqueAnsweredQuestions.toLocaleString('ja-JP')}問に取り組んだ記録を確認。`
      : 'これからの学習記録を使って、推奨ルートとの差を更新します。';

    const planCard = document.createElement('article');
    planCard.className = 'card lt-exam-plan-card';
    planCard.innerHTML = `
      <div class="lt-exam-plan-heading">
        <div>
          <span class="lt-paid-badge">完全版</span>
          <h2>🧭 合格までの推奨ルート</h2>
        </div>
        <strong class="lt-route-pace">${scheduleLabel}</strong>
      </div>
      <p class="lt-route-lead">残り${Number.isFinite(countdownNumber) ? `${countdownNumber}日` : '日数'}を、今の現在地から逆算して進めます。学習結果に合わせてルートは更新されます。</p>
      <div class="lt-route-pace-panel">
        <div><small>この時点の推奨</small><strong>${recommendedDisplay}</strong><span>LT学習到達指標</span></div>
        <div><small>現在</small><strong>${currentDisplay}</strong><span>推奨との差 ${gapDisplay}</span></div>
        <div class="lt-route-pace-result"><small>推奨ルートとの位置</small><strong>${scheduleDetail}</strong><span>${scheduleLabel}</span></div>
      </div>
      <p class="lt-route-evidence">${activityCopy} <b>回答数だけではなく、修復・再確認・定着まで含めて現在地を判定します。</b></p>
      <div class="lt-route-now-grid">
        <div><small>現在地</small><strong>${currentHeadline}</strong></div>
        <div><small>いま優先</small><strong>${priorityField}</strong><span>${priorityLabel}</span></div>
        <div><small>今日やる</small><strong>${todayAmount}</strong></div>
      </div>
      <div class="lt-route-timeline" aria-label="合格までの推奨ルート">
        <div class="is-now"><i></i><span>今週</span><b>${priorityField}を優先</b><small>今日の学習を積み上げ、修復対象を減らす</small></div>
        <div><i></i><span>1か月後</span><b>修復した知識を再確認へ</b><small>その場で解けただけではなく、時間を空けても答えられるか確認</small></div>
        <div><i></i><span>3か月後</span><b>主要弱点を絞り込む</b><small>未確認領域を減らし、定着確認の比率を上げる</small></div>
        <div><i></i><span>試験2か月前</span><b>実戦形式＋残った弱点</b><small>本番を意識した問題と、最後まで残る弱点を再修復</small></div>
        <div class="is-goal"><i></i><span>試験日</span><b>合格を目指す</b><small>確認済み・定着した知識を本番で使える状態へ</small></div>
      </div>
      <div class="lt-route-judgement"><b>${weeklyLabel}：</b><span>${weeklyCopy}</span></div>
      <small class="lt-route-disclaimer">※ 推奨値はLTの学習到達指標に対する目安で、合格確率ではありません。実データを見ながら今後も調整します。</small>`;
    stack.appendChild(planCard);
  }

  if (overallCard && !overallCard.querySelector('.lt-product-meaning')) {
    const progress = text(overallCard.querySelector('.ring span')) || '--';
    const coverage = text(overallCard.querySelector('.overall-progress-metrics div:nth-child(1) dd')) || '--';
    const repaired = text(overallCard.querySelector('.overall-progress-metrics div:nth-child(2) dd')) || '--';
    const stable = text(overallCard.querySelector('.overall-progress-metrics div:nth-child(3) dd')) || '--';
    const box = document.createElement('div');
    box.className = 'lt-product-meaning lt-overall-meaning';
    box.innerHTML = `
      <h3>この到達度が示していること</h3>
      <p><b>現在 ${progress}</b>。単純な正答率ではなく、「どこまで触れたか」「間違いを直せたか」「時間を空けても定着しているか」をまとめたLTの学習到達指標です。</p>
      <div class="lt-meaning-grid">
        <div><span>いま広げている範囲</span><strong>${coverage}</strong><small>まだ触れていない知識を減らす</small></div>
        <div><span>直せた知識</span><strong>${repaired}</strong><small>誤答を別問題で確認する</small></div>
        <div><span>定着を確認できた知識</span><strong>${stable}</strong><small>時間を空けても答えられる状態へ</small></div>
      </div>
      <p class="lt-next-line"><b>今の次の一手：</b>${priorityField}を優先し、修復と再確認を進めます。</p>`;
    overallCard.appendChild(box);
  }

  if (currentCard && !currentCard.querySelector('.lt-current-meaning')) {
    const box = document.createElement('div');
    box.className = 'lt-product-meaning lt-current-meaning';
    box.innerHTML = `
      <h3>LTの判断</h3>
      <p>今は「点数を増やす」より、間違えた知識を直して<b>再現できる状態に変えること</b>を優先する段階です。</p>
      <p><b>この段階を抜ける条件：</b>修復した内容を別問題で確認し、さらに時間を空けた再確認でも答えられること。</p>`;
    currentCard.appendChild(box);
  }

  if (attentionCard && !attentionCard.querySelector('.lt-attention-meaning')) {
    const box = document.createElement('div');
    box.className = 'lt-product-meaning lt-attention-meaning';
    box.innerHTML = `
      <h3>なぜ今ここを優先するのか</h3>
      <p><b>${priorityField}</b>は現在「${priorityLabel}」の状態です。${priorityMessage}</p>
      <p>LTは弱点を並べるだけでなく、<b>今やると効果が高い順</b>に優先順位を付けます。</p>`;
    attentionCard.appendChild(box);
  }

  if (todayCard && !todayCard.querySelector('.lt-today-outcome')) {
    const box = document.createElement('div');
    box.className = 'lt-product-meaning lt-today-outcome';
    box.innerHTML = `
      <h3>今日これをやる理由</h3>
      <p><b>${todayAmount}</b>。${todayReason}</p>
      <div class="lt-action-flow"><span>今日やる</span><i>→</i><span>理解を確認</span><i>→</i><span>必要なら修復</span><i>→</i><span>後日もう一度確認</span></div>
      <p class="lt-next-line"><b>今日終えたら：</b>結果を学習履歴へ反映し、次に優先する内容をLTが更新します。</p>`;
    todayCard.appendChild(box);
  }

  if (weeklyCard && !weeklyCard.querySelector('.lt-weekly-meaning')) {
    let judgement = '学習量だけでなく、修復・再確認・定着がどう進んだかを一緒に見ます。';
    if (progressDelta !== null && progressDelta > 0.2) judgement = `7日間で到達度が ${progressDelta.toFixed(1)}pt 上がりました。取り組んだ量が、学習範囲・修復・定着の前進につながっています。`;
    else if (progressDelta !== null && progressDelta >= -0.2) judgement = '到達度は大きく動いていません。問題数を増やすだけでなく、修復や再確認を進めることが次の伸びにつながります。';
    else if (progressDelta !== null) judgement = '到達度が一時的に下がっています。再確認の時期に入り、覚えたままかを厳しく見直している可能性があります。';
    const box = document.createElement('div');
    box.className = 'lt-product-meaning lt-weekly-meaning';
    box.innerHTML = `<h3>この7日間をLTはこう見ています</h3><p>${judgement}</p><p><b>次の焦点：</b>${priorityField}を優先し、「やった量」から「定着した知識」へ変えていきます。</p>`;
    weeklyCard.appendChild(box);
  }
});
