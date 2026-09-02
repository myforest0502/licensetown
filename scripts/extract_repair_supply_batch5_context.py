import json
from pathlib import Path

ids = ['Q410','Q419','Q1580','Q491','Q617','Q1225','Q1363','Q807','Q820','Q903','Q1054','Q1057','Q1089','Q1111','Q1156','Q1162','Q1281','Q1341','Q954','Q1358','Q1535','Q1519','Q1540']
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
Path('docs/repair-supply-phase2-batch5-source-context.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
