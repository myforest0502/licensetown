document.querySelectorAll('.tab').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach((tab) => tab.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach((panel) => panel.classList.remove('active'));
    button.classList.add('active');
    document.getElementById(button.dataset.tab).classList.add('active');
  });
});

const metricSettings = {
  accuracy: { suffix: '%', summary: '68%', scale: 1 },
  questions: { suffix: '問', summary: '18問/日', scale: 3 },
  minutes: { suffix: '分', summary: '31分/日', scale: 2 },
};
document.querySelectorAll('.metric-tab').forEach((button) => button.addEventListener('click', () => {
  document.querySelectorAll('.metric-tab').forEach((tab) => tab.classList.remove('active'));
  button.classList.add('active');
  const key = button.dataset.metric;
  const setting = metricSettings[key];
  document.querySelector('[data-week-summary]').textContent = setting.summary;
  document.querySelectorAll('[data-week-chart] > div').forEach((item) => {
    const value = Number(item.dataset[key]);
    item.querySelector('span').textContent = `${value}${setting.suffix}`;
    item.querySelector('i').style.height = `${Math.min(value * setting.scale, 100)}%`;
  });
}));

const examDialog = document.getElementById('exam-dialog');
document.querySelector('[data-dialog-open]')?.addEventListener('click', () => examDialog.showModal());
document.querySelector('[data-dialog-close]')?.addEventListener('click', () => examDialog.close());
document.querySelectorAll('[data-close]').forEach((button) => button.addEventListener('click', () => {
  if (window.liff?.isInClient()) window.liff.closeWindow();
  else if (history.length > 1) history.back();
}));

document.querySelectorAll('[data-line-message]').forEach((button) => button.addEventListener('click', () => {
  const message = button.dataset.lineMessage;
  if (window.liff?.isInClient()) {
    window.liff.sendMessages([{ type: 'text', text: message }]).then(() => window.liff.closeWindow());
    return;
  }
  window.location.href = `https://line.me/R/msg/text/?${encodeURIComponent(message)}`;
}));
