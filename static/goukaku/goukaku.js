document.querySelectorAll('.tab').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach((tab) => tab.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach((panel) => panel.classList.remove('active'));
    button.classList.add('active');
    document.getElementById(button.dataset.tab).classList.add('active');
    if (button.dataset.tab === 'graphs') renderComboCharts();
  });
});

function renderComboCharts() {
  document.querySelectorAll('[data-combo-chart]').forEach((chart) => {
    const items = [...chart.querySelectorAll('.chart-item')];
    if (!items.length || !chart.clientWidth) return;
    const bars = items.map((item) => Number(item.dataset.bar) || 0);
    const lines = items.map((item) => item.dataset.line === '' ? null : Number(item.dataset.line));
    const maxBar = Math.max(...bars, 1);
    const numericLines = lines.filter((value) => value !== null);
    const maxLine = Math.max(...numericLines, 1);
    items.forEach((item, index) => {
      item.querySelector('.chart-bar').style.height = `${Math.max((bars[index] / maxBar) * 78, bars[index] ? 5 : 0)}%`;
    });
    const svg = chart.querySelector('.chart-line');
    const width = chart.scrollWidth;
    const height = chart.clientHeight - 52;
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.style.width = `${width}px`;
    const points = [];
    lines.forEach((value, index) => {
      if (value === null) return;
      const item = items[index];
      points.push(`${item.offsetLeft + item.offsetWidth / 2},${height - (value / maxLine) * (height - 18)}`);
    });
    const line = points.length > 1
      ? `<polyline points="${points.join(' ')}" fill="none" stroke="#f29b19" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`
      : '';
    const dots = points.map((point) => {
      const [cx, cy] = point.split(',');
      return `<circle cx="${cx}" cy="${cy}" r="4" fill="#f29b19" stroke="#fff" stroke-width="2"/>`;
    }).join('');
    svg.innerHTML = line + dots;
  });
}

window.addEventListener('resize', () => {
  if (document.getElementById('graphs')?.classList.contains('active')) renderComboCharts();
});

const examDialog = document.getElementById('exam-dialog');
document.querySelector('[data-dialog-open]')?.addEventListener('click', () => examDialog.showModal());
document.querySelector('[data-dialog-close]')?.addEventListener('click', () => examDialog.close());
document.querySelectorAll('[data-close]').forEach((button) => button.addEventListener('click', () => {
  if (window.liff?.isInClient()) window.liff.closeWindow();
  else if (history.length > 1) history.back();
}));

document.querySelectorAll('[data-line-message]').forEach((button) => button.addEventListener('click', () => {
  const message = button.dataset.lineMessage;
  const accountId = button.closest('[data-line-account-id]')?.dataset.lineAccountId;
  if (!accountId) return;
  window.location.href = `https://line.me/R/oaMessage/${encodeURIComponent(accountId)}/?${encodeURIComponent(message)}`;
}));
