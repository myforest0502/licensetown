from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'data'/'question_bank'
TARGETS=ROOT/'reports'/'question_bank_2000_lot05_targets_v01.json'
OUT=ROOT/'reports'/'question_bank_2000_lot05_c7_alternatives.json'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    questions={x['id']:x for x in read(BANK/'questions.json')}
    tags={x['id']:x for x in read(BANK/'question_tags.json')}
    nodes=read(BANK/'knowledge_nodes.json')
    selected={x['canonical_node_id'] for x in read(TARGETS)['existing_node_targets']}
    rows=[]
    for node in nodes:
        nid=node['knowledge_node_id']
        qids=list(node.get('question_ids',[]))
        if nid in selected or len(qids)!=1: continue
        qid=qids[0]
        if qid not in questions or int(questions[qid]['category_small'])!=7: continue
        label=str(node.get('label') or tags[qid].get('knowledge_node') or '')
        if any(x in label for x in ('正解として扱った問題','第54回午前93問')): continue
        rows.append({
            'knowledge_node_id':nid,
            'label':label,
            'question_id':qid,
            'task':tags[qid]['task'],
            'primary_ability':tags[qid]['primary_ability'],
            'level':tags[qid]['level'],
            'safety':tags[qid]['safety'],
            'source':tags[qid]['source'],
        })
    rows.sort(key=lambda x:(x['task']!='fact_recall', x['source']!='past_exam', int(x['question_id'][1:])))
    OUT.write_text(json.dumps(rows[:20],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(rows[:10],ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
