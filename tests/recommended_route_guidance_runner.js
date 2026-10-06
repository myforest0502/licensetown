// Execute the actual browser asset without duplicating its presentation logic.
const fs = require('node:fs');
const vm = require('node:vm');
const snapshot = JSON.parse(fs.readFileSync(0, 'utf8'));
const created = [];
let listener;
let clicked = false;
const existingStart = { hasAttribute: () => Boolean(snapshot.preview), click: () => { clicked = true; } };
const button = { removed: false, addEventListener: (_, callback) => { button.click = callback; }, remove: () => { button.removed = true; } };
const element = () => ({ textContent: '', children: [], appendChild(child) { this.children.push(child); },
  querySelector: () => button, className: '', innerHTML: '' });
const date = element();
date.parentNode = { insertBefore: () => {} };
const today = { querySelector: selector => selector === 'h2' ? {textContent: '既存分野を10問'}
  : selector === 'p' ? {textContent: '既存の理由'}
  : selector === '.learner-nav-action, .recommend-challenge' ? existingStart : {},
  closest: () => snapshot.preview ? {} : null };
const current = { querySelector: () => ({textContent: '既存の現在地'}) };
const overall = { querySelector: () => ({}) };
const cards = { '.date-card': date, '.learner-current-card': current,
  '.learner-today-card': today, '.overall-progress-preview': overall };
const sandbox = { window: { LT_ROUTE_SNAPSHOT: snapshot }, document: {
  addEventListener: (_, callback) => { listener = callback; },
  querySelector: selector => cards[selector] || null,
  createElement: () => { const el = element(); created.push(el); return el; },
}};
vm.runInNewContext(fs.readFileSync('static/goukaku/dashboard-product-copy-v01.js', 'utf8'), sandbox);
listener();
if (button.click) button.click();
const model = sandbox.window.LTRecommendedRoute.build({ daysUntilExam: snapshot.daysUntilExam,
  finish: snapshot.overall?.progress_raw == null ? null : snapshot.overall.progress_raw * 100,
  coverage: snapshot.overall?.coverage_raw == null ? null : snapshot.overall.coverage_raw * 100,
  accuracy: snapshot.accuracy, recommendedAccuracy: snapshot.recommendedAccuracy,
  recommendedCoverage: snapshot.recommendedCoverage });
process.stdout.write(JSON.stringify({ model, html: created.find(el => el.className === 'card lt-exam-plan-card').innerHTML,
  glance: date.children[0].innerHTML, clicked, buttonRemoved: button.removed }));
