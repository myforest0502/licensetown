import json
from pathlib import Path
ids=['Q976','Q998','Q1039','Q1495','Q1500']
base=Path('data/question_bank')
files=['questions.json','answers.json','explanations.json','question_tags.json']
loaded={f:{str(x['id']):x for x in json.loads((base/f).read_text(encoding='utf-8-sig'))} for f in files}
lines=['# Repair Supply Phase2 batch10 top5 source context','']
for qid in ids:
    q=loaded['questions.json'][qid]; a=loaded['answers.json'][qid]; e=loaded['explanations.json'][qid]; t=loaded['question_tags.json'][qid]
    lines += [f'## {qid} / {t.get("knowledge_node_id")}',f'- management: {q.get("management_code")}',f'- task/ability: {t.get("task")} / {t.get("primary_ability")}',f'- secondary: {t.get("secondary_ability")}',f'- safety: {t.get("safety")}',f'- node: {t.get("knowledge_node")}',f'- stem: {q.get("question_text")}',f'- choices: {q.get("choices")}',f'- answer: {a.get("display_answer")}',f'- accepted: {a.get("accepted_answer_sets")}',f'- explanation: {e.get("explanation")}', '']
Path('docs/repair-supply-phase2-batch10-top5-source-context.md').write_text('\n'.join(lines),encoding='utf-8')
