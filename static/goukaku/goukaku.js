document.querySelectorAll('.tab').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach((tab) => tab.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach((panel) => panel.classList.remove('active'));
    button.classList.add('active');
    document.getElementById(button.dataset.tab).classList.add('active');
  });
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
  if (window.liff?.isInClient()) {
    window.liff.sendMessages([{ type: 'text', text: message }]).then(() => window.liff.closeWindow());
    return;
  }
  window.location.href = `https://line.me/R/msg/text/?${encodeURIComponent(message)}`;
}));
