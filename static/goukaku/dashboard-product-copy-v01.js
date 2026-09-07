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

  const countdownNumber = Number((text(dateCard?.querySelector('.countdown strong')) || '').replace(/[^0-9]/g, ''));
  let paceLabel = '進み方を確認中';
  let paceCopy = '学習履歴が増えるほど、推奨ルートとのズレを細かく確認できるようになります。';
  if (progressDelta !== null && progressDelta > 0.2) {
    paceLabel = '今週は前進中';
    paceCopy = `直近7日間で到達度が ${progressDelta.toFixed(1)}pt 上がっています。今の優先分野を続けながら、修復した知識を再確認へつなげます。`;
  } else if (progressDelta !== null && progressDelta >= -0.2) {
    paceLabel = '今週は足場固め';
    paceCopy = '到達度は大きく動いていません。問題数だけを増やさず、修復と再確認を進める時期です。';
  } else if (progressDelta !== null) {
    paceLabel = '再確認フェーズ';
    paceCopy = '到達度が一時的に下がっています。覚えたままかを厳しく見直している可能性があります。';
  }

  if (dateCard && overallCard && currentCard && todayCard && !document.querySelector('.lt-top-left-stack')) {
    const stack = document.createElement('section');
    stack.className = 'lt-top-left-stack';
    dateCard.parentNode.insertBefore(stack, dateCard);
    stack.appendChild(dateCard);

    const planCard = document.createElement('article');
    planCard.className = 'card lt-exam-plan-card';
    planCard.innerHTML = `
      <div class="lt-exam-plan-heading">
        <div>
          <span class="lt-paid-badge">完全版</span>
          <h2>🧭 合格までの推奨ルート</h2>
        </div>
        <strong class="lt-route-pace">${paceLabel}</strong>
      </div>
      <p class="lt-route-lead">残り${Number.isFinite(countdownNumber) ? `${countdownNumber}日` : '日数'}を、今の現在地から逆算して進めます。学習結果に合わせてルートは更新されます。</p>
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
      <div class="lt-route-judgement"><b>今の進み方：</b><span>${paceCopy}</span></div>`;
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
