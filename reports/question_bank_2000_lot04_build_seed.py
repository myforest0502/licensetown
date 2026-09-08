"""Build a non-final Lot04 authoring seed by combining template and quota-exact suggestions."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/'staging'/'question_bank_2000_lot04_template_v01.json'
ASSIGNMENT=ROOT/'reports'/'question_bank_2000_lot04_assignment_v01.json'
OUT=ROOT/'staging'/'question_bank_2000_lot04_authoring_seed_v01.json'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def main():
    template=read(TEMPLATE); assignment=read(ASSIGNMENT)
    if template.get('formal_baseline')!='Q1-Q1905' or assignment.get('formal_baseline')!='Q1-Q1905': raise ValueError('Lot04 template/assignment baseline mismatch')
    by_id={r['draft_id']:r for r in assignment['assignments']}; drafts=[]
    for original in template['drafts']:
        draft=json.loads(json.dumps(original,ensure_ascii=False)); s=by_id[draft['draft_id']]
        draft['proposed_task']=s['suggested_task']; draft['primary_ability']=s['suggested_primary_ability']; draft['level']=s['suggested_level']; draft['safety']=s['suggested_safety']; draft['assignment_status']='suggested_not_editorially_approved'; draft['assignment_may_change_if_quotas_preserved']=True
        draft['semantic_review']['candidate_demand']=f"suggested {s['suggested_task']} / {s['suggested_primary_ability']}"
        if not s['is_new']:
            draft['semantic_review']['reference_demand']='existing demands: '+', '.join(f"{x['task']}/{x['primary_ability']}" for x in s['existing_demands'])
        drafts.append(draft)
    if len(drafts)!=48 or len({d['draft_id'] for d in drafts})!=48: raise ValueError('Lot04 seed must contain 48 unique drafts')
    output={**{k:v for k,v in template.items() if k!='drafts'},'batch':'question_bank_2000_production_lot04_v01','status':'authoring_seed_only','drafts':drafts,'seed_warning':'Suggested task/level/Safety values are structural aids only; medical authoring may change them if final quotas remain exact.'}
    OUT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print({'drafts':48,'output':str(OUT.relative_to(ROOT))}); return 0
if __name__=='__main__': raise SystemExit(main())
