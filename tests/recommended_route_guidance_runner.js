// Execute the actual browser asset with a small DOM stub.
const fs = require('node:fs');
const vm = require('node:vm');
const snapshot = JSON.parse(fs.readFileSync(0, 'utf8'));
const created = [];
let listener;
const element = () => ({
  textContent: '', children: [], className: '', innerHTML: '',
  appendChild(child) { this.children.push(child); },
  querySelector() { return { textContent: '' }; }
});
const date = element();
date.parentNode = { insertBefore: () => {} };
date.querySelector = selector => selector === '.countdown strong'
  ? { textContent: snapshot.daysUntilExam == null ? '' : String(snapshot.daysUntilExam) }
  : { textContent: '' };
const today = { children: [], appendChild(child) { this.children.push(child); }, querySelector: selector => selector === 'h2' ? { textContent: '理学療法治療各論を10問' }
  : selector === 'p' ? { textContent: '既存の理由' } : null };
const current = { querySelector: () => ({ textContent: 'まず大事なところを確認しよう' }) };
const attention = { children: [], appendChild(child) { this.children.push(child); }, querySelector: () => null };
const overall = { querySelector: () => ({ textContent: '' }) };
const weekly = { children: [], appendChild(child) { this.children.push(child); }, querySelector: () => null };
const cards = {
  '.date-card': date,
  '.learner-current-card': current,
  '.learner-attention-card': attention,
  '.learner-today-card': today,
  '.overall-progress-preview': overall,
  '.weekly-learning-card': weekly,
};
const sandbox = {
  window: { LT_ROUTE_SNAPSHOT: snapshot, LT_WEEKLY_LEARNING_SNAPSHOT: { overallProgress: [] } },
  document: {
    addEventListener: (_, callback) => { listener = callback; },
    querySelector: selector => selector === '.lt-top-left-stack' ? null : (cards[selector] || null),
    createElement: () => { const el = element(); created.push(el); return el; },
  }
};
vm.runInNewContext(fs.readFileSync('static/goukaku/dashboard-product-copy-v01.js', 'utf8'), sandbox);
listener();
const plan = created.find(el => el.className === 'card lt-exam-plan-card');
process.stdout.write(JSON.stringify({ html: plan ? plan.innerHTML : '' }));
