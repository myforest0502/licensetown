const quiz = document.querySelector('[data-web-quiz]');
const answerButton = quiz?.querySelector('[data-submit-answer]');
const unknownButton = quiz?.querySelector('[data-submit-unknown]');
const status = quiz?.querySelector('[data-web-quiz-status]');

async function submitWebAnswer(unknown) {
  const actionButtons = [answerButton, unknownButton].filter(Boolean);
  actionButtons.forEach((button) => { button.disabled = true; });
  if (status) status.textContent = '採点しています…';
  try {
    const selectedAnswers = unknown
      ? []
      : [...quiz.querySelectorAll('input[name="answer"]:checked')].map((input) => input.value);
    const confidenceInput = quiz.querySelector('input[name="confidence"]:checked');
    const response = await fetch(quiz.dataset.answerUrl, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question_id: quiz.dataset.questionId,
        selected_answers: selectedAnswers,
        confidence: confidenceInput ? Number(confidenceInput.value) : null,
        unknown,
      }),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.ok) throw new Error(result.message || '採点できませんでした。');
    quiz.querySelector('[data-result-mark]').textContent = result.is_correct ? '○ 正解！' : '× もう一度確認しよう';
    quiz.querySelector('[data-selected-answer]').textContent = result.selected_answer;
    quiz.querySelector('[data-correct-answer]').textContent = result.correct_answer;
    quiz.querySelector('[data-explanation]').textContent = `解説：${result.explanation}`;
    const choiceDetails = quiz.querySelector('[data-choice-explanations]');
    choiceDetails.replaceChildren(...Object.entries(result.choice_explanations || {}).map(([label, text]) => {
      const paragraph = document.createElement('p');
      paragraph.textContent = `${label}：${text}`;
      return paragraph;
    }));
    quiz.querySelector('[data-web-quiz-result]').hidden = false;
    quiz.querySelectorAll('fieldset, .web-quiz-actions').forEach((element) => { element.hidden = true; });
    quiz.querySelector('[data-next-question]').textContent = result.completed ? '結果を見る' : '次の問題へ';
    if (status) status.textContent = '学習履歴へ保存しました。';
  } catch (error) {
    if (status) status.textContent = error.message || '回答を送信できませんでした。';
    actionButtons.forEach((button) => { button.disabled = false; });
  }
}

answerButton?.addEventListener('click', () => submitWebAnswer(false));
unknownButton?.addEventListener('click', () => submitWebAnswer(true));
quiz?.querySelector('[data-next-question]')?.addEventListener('click', () => window.location.reload());
