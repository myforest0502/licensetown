"""Aggregate fail-closed pre-seal audit for Question Bank 2000 Lot04."""
from __future__ import annotations
import json, re, unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from reports.question_bank_2000_lot04_chunk_validate import build_report
ROOT=Path(__file__).resolve().parents[1]
CHUNK_DIR=ROOT/'staging'/'question_bank_2000_lot04_chunks_v01'
AUDIT_DIR=ROOT/'reports'/'question_bank_2000_lot04_similarity_audits'
BANK=ROOT/'data'/'question_bank'
OUT=ROOT/'reports'/'question_bank_2000_lot04_preseal_audit.json'
EXPECTED_CATEGORY={1:4,2:5,3:2,4:2,5:2,6:3,7:3,8:6,9:2,10:2,11:3,12:2,13:3,14:2,15:4,17:1,18:2}
EXPECTED_TASK={'assessment_selection':9,'device_selection':2,'fact_recall':2,'finding_interpretation':14,'functional_goal_decision':4,'intervention_selection':8,'prognosis_prediction':3,'safety_priority':6}
EXPECTED_LEVEL={1:2,2:16,3:20,4:10}
EXPECTED_SLOT={'singleton_second':27,'multi_reinforcement':17,'new_node':4}
EXPECTED_SAFETY=12
MIN_STRONG=37

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def norm(s): return re.sub(r'[^0-9a-zぁ-んァ-ヶ一-龠々ー]+','',unicodedata.normalize('NFKC',str(s or '')).lower())
def main():
    errors=[]; warnings=[]; drafts=[]; similarity={}
    for n in range(1,7):
        p=CHUNK_DIR/f'chunk_{n:02d}.json'; payload=read(p); report=build_report(payload)
        errors += [f'chunk{n:02d}: {x}' for x in report['hard_errors']]
        drafts += payload.get('drafts',[])
        ap=AUDIT_DIR/f'chunk_{n:02d}.json'
        if not ap.exists(): errors.append(f'chunk{n:02d}: missing similarity audit'); continue
        a=read(ap); similarity[n]={'exact':a.get('exact_total'),'hard_near':a.get('hard_near_total'),'near':a.get('near_total')}
        if a.get('exact_total') or a.get('hard_near_total'): errors.append(f'chunk{n:02d}: similarity gate failed {similarity[n]}')
    if len(drafts)!=48 or len({d.get('draft_id') for d in drafts})!=48: errors.append(f'expected 48 unique drafts, got {len(drafts)}')
    category=Counter(int(d['proposed_category_small']) for d in drafts); task=Counter(d['proposed_task'] for d in drafts); level=Counter(int(d['level']) for d in drafts); slot=Counter(d['slot_type'] for d in drafts)
    safety=sum(d.get('safety') in {'moderate','critical'} for d in drafts)
    strong=0
    for d in drafts:
        if d.get('slot_type')=='new_node': continue
        existing={(str(x.get('task')),str(x.get('primary_ability'))) for x in d.get('existing_demands',[])}
        if (str(d.get('proposed_task')),str(d.get('primary_ability'))) not in existing: strong+=1
    for name,actual,expected in [('category',category,Counter(EXPECTED_CATEGORY)),('task',task,Counter(EXPECTED_TASK)),('level',level,Counter(EXPECTED_LEVEL)),('slot',slot,Counter(EXPECTED_SLOT))]:
        if actual!=expected: errors.append(f'{name} quota mismatch: actual={dict(actual)} expected={dict(expected)}')
    if safety!=EXPECTED_SAFETY: errors.append(f'safety moderate/critical mismatch: actual={safety} expected={EXPECTED_SAFETY}')
    if strong<MIN_STRONG: errors.append(f'structural strong below minimum: {strong} < {MIN_STRONG}')
    nodes=read(BANK/'knowledge_nodes.json'); existing_labels=[(x.get('knowledge_node_id'),x.get('label',''),norm(x.get('label',''))) for x in nodes]
    new_rows=[d for d in drafts if d.get('slot_type')=='new_node']; collision=[]
    for d in new_rows:
        nl=norm(d.get('target_node_label')); ranked=[]
        for nid,label,n in existing_labels:
            if not n: continue
            score=SequenceMatcher(None,nl,n,autojunk=False).ratio(); ranked.append((score,nid,label))
        ranked.sort(reverse=True); top=ranked[:5]
        collision.append({'draft_id':d['draft_id'],'label':d['target_node_label'],'top_existing':[{'node_id':nid,'score':round(score,6),'label':label} for score,nid,label in top]})
        if top and top[0][0]>=0.82: errors.append(f"{d['draft_id']}: new Node label collision score {top[0][0]:.3f} with {top[0][1]}")
        elif top and top[0][0]>=0.68: warnings.append(f"{d['draft_id']}: review Node label similarity {top[0][0]:.3f} with {top[0][1]}")
    payload={'hard_errors':errors,'warnings':warnings,'draft_count':len(drafts),'category_counts':dict(category),'task_counts':dict(task),'level_counts':dict(level),'slot_counts':dict(slot),'safety_moderate_or_critical':safety,'structural_strong_formations':strong,'similarity':similarity,'new_node_collision':collision}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(payload,ensure_ascii=False,indent=2)); return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
