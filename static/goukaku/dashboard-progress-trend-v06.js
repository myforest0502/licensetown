document.addEventListener('DOMContentLoaded', () => {
  const weekly = window.LT_WEEKLY_LEARNING_SNAPSHOT || {};
  const points = Array.isArray(weekly.overallProgress) ? weekly.overallProgress : [];
  const card = document.querySelector('.weekly-learning-card');
  const spark = card?.querySelector('.weekly-spark');
  if (!card || !spark || points.length < 2) return;

  const values = points.map((item) => Number(item.progress) || 0);
  const observedMin = Math.min(...values);
  const observedMax = Math.max(...values);
  let min = Math.max(0, Math.floor(observedMin) - 1);
  let max = Math.min(100, Math.ceil(observedMax) + 1);
  if (max - min < 4) {
    const center = (max + min) / 2;
    min = Math.max(0, Math.floor(center - 2));
    max = Math.min(100, Math.ceil(center + 2));
    if (max - min < 4) max = Math.min(100, min + 4);
  }
  const range = Math.max(max - min, 1);
  const width = 700;
  const top = 18;
  const bottom = 96;
  const xStep = width / points.length;
  const coords = points.map((item, index) => {
    const value = Number(item.progress) || 0;
    const x = (xStep * index) + (xStep / 2);
    const y = bottom - ((value - min) / range) * (bottom - top);
    return { x, y, value, label: item.label || '' };
  });
  const polyline = coords.map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(' ');
  const nodes = coords.map((point) => `
    <g>
      <circle cx="${point.x}" cy="${point.y}" r="4.5"></circle>
      <text x="${point.x}" y="${Math.max(point.y - 9, 11)}" text-anchor="middle">${point.value.toFixed(1)}%</text>
    </g>`).join('');

  const combined = document.createElement('div');
  combined.className = 'weekly-combined-chart';
  spark.parentNode.insertBefore(combined, spark);
  combined.appendChild(spark);

  const overlay = document.createElement('div');
  overlay.className = 'weekly-progress-overlay';
  overlay.innerHTML = `
    <svg viewBox="0 0 ${width} 112" preserveAspectRatio="none" role="img" aria-label="直近7日間の合格への到達度推移">
      <line class="weekly-progress-gridline" x1="0" x2="${width}" y1="${top}" y2="${top}"></line>
      <line class="weekly-progress-gridline" x1="0" x2="${width}" y1="${bottom}" y2="${bottom}"></line>
      <polyline class="weekly-progress-line" points="${polyline}"></polyline>
      ${nodes}
    </svg>
    <span class="weekly-progress-scale top">${max}%</span>
    <span class="weekly-progress-scale bottom">${min}%</span>`;
  combined.appendChild(overlay);

  const first = coords[0]?.value || 0;
  const last = coords[coords.length - 1]?.value || 0;
  const delta = Math.round((last - first) * 10) / 10;
  const sign = delta > 0 ? '+' : '';
  const legend = document.createElement('div');
  legend.className = 'weekly-combined-legend';
  legend.innerHTML = `
    <span><i class="bar-mark"></i>回答数</span>
    <span><i class="line-mark"></i>合格への到達度</span>
    <strong>7日間：${first.toFixed(1)}% → ${last.toFixed(1)}%（${sign}${delta.toFixed(1)}pt）</strong>`;
  combined.insertAdjacentElement('beforebegin', legend);

  const note = document.createElement('p');
  note.className = 'weekly-progress-note';
  note.textContent = '棒はその日の回答数、折れ線はその時点の「合格への到達度」です。到達度は問題数だけでなく、学習範囲・修復・再確認・定着で動きます。';
  combined.insertAdjacentElement('afterend', note);
});
