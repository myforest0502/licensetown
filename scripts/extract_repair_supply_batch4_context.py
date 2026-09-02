import json
from pathlib import Path

ids = ['Q1420','Q686','Q2','Q1493','Q65']
base = Path('data/question_bank')
files = ['questions.json','answers.json','explanations.json','question_tags.json']
loaded = {name: json.loads((base/name).read_text(encoding='utf-8-sig')) for name in files}
indexes = {name: {str(item['id']): item for item in rows} for name, rows in loaded.items()}
out = {'targets': []}
for qid in ids:
    out['targets'].append({
        'question_id': qid,
        'question': indexes['questions.json'][qid],
        'answer': indexes['answers.json'][qid],
        'explanation': indexes['explanations.json'][qid],
        'tag': indexes['question_tags.json'][qid],
    })
Path('docs/repair-supply-phase2-batch4-source-context.json').write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8'
)
