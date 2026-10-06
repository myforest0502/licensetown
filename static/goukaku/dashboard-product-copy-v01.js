// Read-only presentation: the existing finish curve remains the sole pace calculation.
window.LTRecommendedRoute = (() => {
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


  const percent = (value) => {
    if (value === null || value === undefined || value === '' || typeof value === 'boolean') return null;
    const number = Number(value);
    return Number.isFinite(number) && number >= 0 && number <= 100 ? number : null;
  };
  const gap = (current, recommended) => current === null || recommended === null
    ? null : Math.max(0, recommended - current);
  const build = (snapshot) => {
    const days = snapshot.daysUntilExam === null || snapshot.daysUntilExam === undefined
      || snapshot.daysUntilExam === '' || typeof snapshot.daysUntilExam === 'boolean'
      ? null : Number(snapshot.daysUntilExam);
    const remaining = Number.isFinite(days) && days >= 0 ? days : null;
    const finish = percent(snapshot.finish);
    const recommended = interpolateRecommendedProgress(remaining);
    const equivalent = equivalentDaysRemaining(finish);
    const deltaDays = remaining !== null && equivalent !== null ? Math.round(remaining - equivalent) : null;
    const coverage = percent(snapshot.coverage);
    const accuracy = percent(snapshot.accuracy);
    // No date-specific coverage/accuracy targets exist today. Only compare explicit
    // source criteria if supplied; never derive them from the finish curve.
    const coverageTarget = percent(snapshot.recommendedCoverage);
    const accuracyTarget = percent(snapshot.recommendedAccuracy);
    const metrics = [
      { key: 'coverage', label: '学習範囲', current: coverage, recommended: coverageTarget,
        shortage: coverage === 100 ? 0 : gap(coverage, coverageTarget) },
      { key: 'accuracy', label: '正答率', current: accuracy, recommended: accuracyTarget,
        shortage: gap(accuracy, accuracyTarget) },
      { key: 'finish', label: '知識の仕上がり', current: finish, recommended,
        shortage: gap(finish, recommended) },
    ];
    const shortages = metrics.filter(item => item.shortage > 0).sort((a, b) => b.shortage - a.shortage);
    return { remaining, expired: Number.isFinite(days) && days < 0, finish, recommended, deltaDays, metrics, shortages };
  };
  return { build, interpolateRecommendedProgress, equivalentDaysRemaining };
})();

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

  const progressPoints = Array.isArray(window.LT_WEEKLY_LEARNING_SNAPSHOT?.overallProgress)
    ? window.LT_WEEKLY_LEARNING_SNAPSHOT.overallProgress : [];
  const firstProgress = Number(progressPoints[0]?.progress);
  const lastProgress = Number(progressPoints[progressPoints.length - 1]?.progress);
  const progressDelta = Number.isFinite(firstProgress) && Number.isFinite(lastProgress)
    ? Math.round((lastProgress - firstProgress) * 10) / 10 : null;

  const routeSnapshot = window.LT_ROUTE_SNAPSHOT || {};
  const overall = routeSnapshot.overall || {};
  const model = window.LTRecommendedRoute.build({
    daysUntilExam: routeSnapshot.daysUntilExam,
    finish: overall.progress_raw == null ? null : overall.progress_raw * 100,
    coverage: overall.coverage_raw == null ? null : overall.coverage_raw * 100,
    accuracy: routeSnapshot.accuracy,
    recommendedCoverage: routeSnapshot.recommendedCoverage,
    recommendedAccuracy: routeSnapshot.recommendedAccuracy,
  });
  const countdownNumber = model.remaining;
  const currentProgress = model.finish;
  const recommendedProgress = model.recommended;
  const scheduleDeltaDays = model.deltaDays;
  const totalAnswers = Number(routeSnapshot.totalAnswers) || 0;
  const uniqueAnsweredQuestions = Number(routeSnapshot.uniqueAnsweredQuestions) || 0;
  const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[char]));
  const displayPercent = value => value === null ? '記録なし' : `${value.toFixed(1).replace(/\.0$/, '')}%`;

  let scheduleLabel = '推奨ペースを計算中';
  let scheduleDetail = '位置を確認中';
  if (scheduleDeltaDays !== null) {
    if (Math.abs(scheduleDeltaDays) <= 2) {
      scheduleLabel = 'ほぼ予定どおり';
      scheduleDetail = scheduleDeltaDays > 0 ? `約${scheduleDeltaDays}日先行` : scheduleDeltaDays < 0 ? `約${Math.abs(scheduleDeltaDays)}日遅れ` : '予定どおり';
    } else if (scheduleDeltaDays > 0) {
      scheduleLabel = scheduleDeltaDays <= 7 ? '推奨ペース内' : '前倒しで進行';
      scheduleDetail = `約${scheduleDeltaDays}日先行`;
    } else {
      scheduleLabel = '次の学習で差を縮めよう';
      scheduleDetail = `約${Math.abs(scheduleDeltaDays)}日遅れ`;
    }
  }

  let weeklyLabel = '進み方を確認中';
  let weeklyCopy = '学習履歴が増えるほど、推奨ルートとのズレを細かく確認できるようになります。';
  if (progressDelta !== null && progressDelta > 0.2) {
    weeklyLabel = '今週は前進中';
    weeklyCopy = `直近7日間で知識の仕上がりが ${progressDelta.toFixed(1)}pt 上がっています。今の優先分野を続けながら、修復した知識を再確認へつなげます。`;
  } else if (progressDelta !== null && progressDelta >= -0.2) {
    weeklyLabel = '今週は足場固め';
    weeklyCopy = '知識の仕上がりは大きく動いていません。問題数だけを増やさず、修復と再確認を進める時期です。';
  } else if (progressDelta !== null) {
    weeklyLabel = '弱点攻略・再確認中';
    weeklyCopy = `知識の仕上がりは一時的に下がっていますが、単純な後退とは限りません。LTが弱点や再確認が必要な知識を見つけ、${priorityField}を中心に「できる問題を増やす」段階から「苦手を直して定着させる」段階へ進んでいる可能性があります。`;
  }

  if (dateCard && overallCard && currentCard && todayCard && !document.querySelector('.lt-top-left-stack')) {
    const stack = document.createElement('section');
    stack.className = 'lt-top-left-stack';
    dateCard.parentNode.insertBefore(stack, dateCard);
    stack.appendChild(dateCard);
    const countdownCopy = model.expired ? '試験日を過ぎています' : countdownNumber === null ? '試験日は未設定'
      : countdownNumber === 0 ? '今日は試験日' : `試験まであと${countdownNumber}日`;
    const paceCopy = scheduleDeltaDays === null ? '推奨ペースとの位置を確認中'
      : scheduleDeltaDays === 0 ? 'LT推奨ペースと同じ位置です'
      : `LT推奨ペースより${scheduleDetail}${scheduleDeltaDays < 0 ? 'ています' : 'しています'}`;
    const metricHtml = model.metrics.map(item => {
      let status = '今日の推奨基準は未設定';
      let valueLine = item.current === null ? '記録なし' : `現在 ${displayPercent(item.current)}`;

      if (item.key === 'finish') {
        valueLine = '試験日から逆算した今日の目安と比較しています';
        if (item.current === null) status = '学習記録が増えると確認できます';
        else if (item.shortage > 0) {
          status = item.shortage < 0.1
            ? '今日の目安まで0.1pt未満'
            : `今日の目安まであと${item.shortage.toFixed(1).replace(/\.0$/, '')}pt`;
        } else if (item.shortage === 0) status = '今日の目安を満たしています';
        else status = '試験日を設定すると目安を確認できます';
      } else {
        if (item.current === null) status = '学習記録が増えると確認できます';
        else if (item.key === 'coverage' && item.current === 100) status = '十分・不足なし';
        else if (item.shortage > 0) status = item.shortage < 0.1 ? '不足は0.1pt未満' : `あと${item.shortage.toFixed(1).replace(/\.0$/, '')}pt`;
        else if (item.shortage === 0) status = '今日の目安を満たしています';
        else if (item.key === 'coverage') status = `全範囲まであと${(100 - item.current).toFixed(1).replace(/\.0$/, '')}pt`;
        if (item.recommended !== null) valueLine = `推奨 ${displayPercent(item.recommended)} / 現在 ${displayPercent(item.current)}`;
      }

      return `<div class="lt-route-metric" data-route-metric="${item.key}"><h3>${item.label}</h3>
        <p>${valueLine}</p>
        <b class="${item.shortage > 0 ? 'has-shortage' : ''}">${status}</b>
        ${item.key === 'coverage' && item.recommended === null && item.current !== 100 ? '<small>全範囲との比較です。今日の推奨基準は未設定です。</small>' : ''}
        ${item.key === 'finish' ? '<small>厳密な仕上がり率そのものは表示せず、今日必要な水準との差だけを示します。合格確率ではありません。</small>' : ''}</div>`;
    }).join('');

    const focusItem = model.shortages[0];
    const focusCopy = focusItem
      ? `今いちばん足りないもの：${focusItem.label}（${focusItem.shortage < 0.1 ? '今日の目安まで0.1pt未満' : `今日の目安まであと${focusItem.shortage.toFixed(1).replace(/\.0$/, '')}pt`}）`
      : `今日の目安は満たしています。次の焦点：${escapeHtml(priorityLabel)}（${escapeHtml(priorityField)}）`;
    const fields = new Map((routeSnapshot.fields || []).map(item => [item.name, item]));
    // Keep the existing navigation priority order, including Safety/repair/recheck.
    // A low finish score alone must not override the learning strategy.
    const priorities = (routeSnapshot.navigation?.attention_items || []).slice(0, 3);
    const priorityHtml = priorities.length
      ? `<section class="lt-route-priorities"><h3>特に優先する分野</h3><ol>${priorities.map(item => {
        return `<li><b>${escapeHtml(item.field)}</b><span>${escapeHtml(item.label)}</span>
          <small>${escapeHtml(item.message)}</small></li>`;
      }).join('')}</ol></section>` : '';
    const action = routeSnapshot.navigation?.today_action || {};
    const actionCopy = action.field && action.count > 0
      ? `${action.field}を${action.count}問` : todayAmount;
    const actionReason = action.reason || todayReason;
    const intentCopy = { repair: '弱点の修復問題を優先', recheck: '再確認問題を優先',
      exploration: 'まだ確認していない内容を優先' }[action.learning_intent] || '';
    const stateCopy = model.metrics[0].current === 100
      ? '学習範囲は100%まで進んでいます。ここからの優先内容は、今日の学習ナビで確認できます。'
      : '今日の学習ナビに沿って、学習範囲・理解・知識の定着を進めましょう。';

    const planCard = document.createElement('article');
    planCard.className = 'card lt-exam-plan-card';
    planCard.innerHTML = `
      <div class="lt-exam-plan-heading"><div><span class="lt-paid-badge">完全版</span><h2>🧭 合格までの推奨ルート</h2></div></div>
      <div class="lt-route-hero">
        <p class="lt-route-countdown">${countdownCopy}</p>
        <small>現在の位置</small><strong class="lt-route-position">${scheduleDetail}</strong>
        <p>${paceCopy}</p><span>${scheduleLabel}</span>
      </div>
      <p class="lt-route-lead">LT推奨ペースでは、今日の目安はここです。学習結果に合わせてルートを更新します。</p>
      <p class="lt-route-state">${stateCopy}</p>
      <section class="lt-route-status"><h3>今の状態・不足しているポイント</h3><div class="lt-route-metrics">${metricHtml}</div></section>
      <p class="lt-route-focus">${focusCopy}</p>
      ${priorityHtml}
      <section class="lt-route-today"><h3>今日やること</h3><strong>${escapeHtml(actionCopy)}</strong>
        ${intentCopy ? `<b>＋${intentCopy}</b>` : ''}<p>${escapeHtml(actionReason)}</p>
        <button type="button" class="lt-route-start">今日の学習へ</button></section>
      <details class="lt-route-supplement"><summary>判定方法の補足</summary>
        <p>「先行／遅れ」は、試験日から逆算したLTの推奨カーブと現在の知識の仕上がりを比較して算出しています。</p>
        <p>厳密な仕上がり率の絶対値は、この推奨ルートでは表示しません。不足がある場合は「今日の目安まであと○pt」で示します。</p>
        <p>${totalAnswers.toLocaleString('ja-JP')}回答・${uniqueAnsweredQuestions.toLocaleString('ja-JP')}問の記録。回答数だけでなく修復・再確認・定着を含みます。</p>
        <p>${weeklyLabel}：${escapeHtml(weeklyCopy)}</p>
        <small>※ 合格確率ではありません。正答率と学習範囲には日付ごとの推奨基準がまだありません。</small>
      </details>`;
    const startButton = planCard.querySelector('.lt-route-start');
    const existingStart = todayCard.querySelector('.learner-nav-action, .recommend-challenge');
    if (existingStart && !existingStart.hasAttribute('aria-disabled') && !todayCard.closest('[inert]')) {
      startButton.addEventListener('click', () => existingStart.click());
    } else {
      startButton.remove();
    }
    // The approved layout moves the full route below the summary. Keep the two
    // primary facts beside the date at the top, including on small phones.
    const glance = document.createElement('p');
    glance.className = 'lt-route-glance';
    glance.innerHTML = `<span>${countdownCopy}</span><b>${paceCopy}</b>`;
    dateCard.appendChild(glance);
    stack.appendChild(planCard);
  }

  if (overallCard && !overallCard.querySelector('.lt-product-meaning')) {
    const progress = text(overallCard.querySelector('.ring span')) || '--';
    const coverage = text(overallCard.querySelector('.overall-progress-metrics div:nth-child(1) dd')) || '--';
    const accuracy = text(overallCard.querySelector('.overall-progress-metrics div:nth-child(2) dd')) || '--';
    const finish = text(overallCard.querySelector('.overall-progress-metrics div:nth-child(3) dd')) || '--';
    const box = document.createElement('div');
    box.className = 'lt-product-meaning lt-overall-meaning';
    box.innerHTML = `
      <h3>この学習進捗が示していること</h3>
      <p><b>現在 ${progress}</b>。学習範囲・正答率・知識の仕上がりを合わせた学習進捗です。合格確率を表す数値ではありません。</p>
      <div class="lt-meaning-grid">
        <div><span>いま広げている範囲</span><strong>${coverage}</strong><small>まだ触れていない知識を減らす</small></div>
        <div><span>正答率</span><strong>${accuracy}</strong><small>回答した問題での理解を確認する</small></div>
        <div><span>知識の仕上がり</span><strong>${finish}</strong><small>間違いを直し、時間を空けても答えられる状態へ</small></div>
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
    if (progressDelta !== null && progressDelta > 0.2) judgement = `7日間で知識の仕上がりが ${progressDelta.toFixed(1)}pt 上がりました。取り組んだ量が、学習範囲・修復・定着の前進につながっています。`;
    else if (progressDelta !== null && progressDelta >= -0.2) judgement = '知識の仕上がりは大きく動いていません。問題数を増やすだけでなく、修復や再確認を進めることが次の伸びにつながります。';
    else if (progressDelta !== null) judgement = `知識の仕上がりは一時的に下がっていますが、単純な後退とは限りません。今は${priorityField}を中心に、LTが弱点や再確認が必要な知識を見つけて修復・定着へ進めている可能性があります。苦手に挑む時期は数字が下がることもあります。ここを乗り越えて、どの分野にも対応できるPTを目指しましょう。`;
    const box = document.createElement('div');
    box.className = 'lt-product-meaning lt-weekly-meaning';
    box.innerHTML = `<h3>この7日間をLTはこう見ています</h3><p>${judgement}</p><p><b>次の焦点：</b>${priorityField}を優先し、苦手を一つずつ「できる」に変えていきます。目指すのは、どの分野にも対応できるPTです。</p>`;
    weeklyCard.appendChild(box);
  }
});
