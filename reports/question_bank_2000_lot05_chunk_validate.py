"""Fail-closed completeness validator for one Lot05 authoring chunk.

Passing a chunk does not permit Q-ID allocation, Node-ID allocation, sealing, integration,
or formal writes. Final 41-question quotas are enforced later across the merged Lot05.
"""
from __future__ import annotations
import argparse, json, re, unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CHUNK_DIR=ROOT/'staging'/'question_bank_2000_lot05_chunks_v01'
FORBIDDEN={'id','qid','q_id','question_id','reserved_qid','new_question_id','management_code'}
TASK_PRIMARY={
 'assessment_selection':'MEASURE','device_selection':'PRESCRIBE','fact_recall':'KNOW',
 'finding_interpretation':'INTERPRET','functional_goal_decision':'DECIDE',
 'intervention_selection':'PRESCRIBE','prognosis_prediction':'PREDICT','safety_priority':'DECIDE',
}
EXPECTED_SIZES={1:7,2:7,3:7,4:7,5:7,6:6}

def norm(text):
    value=unicodedata.normalize('NFKC',str(text or '')).lower()
    return re.sub(r'[^0-9a-zぁ-んァ-ヶ一-龠々ー]+','',value)

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))

def build_report(payload, chunk_no):
    errors=[]; warnings=[]
    def check(ok,msg):
        if not ok: errors.append(msg)
    check(payload.get('lot')==5,'lot mismatch')
    check(payload.get('chunk')==chunk_no,'chunk number mismatch')
    check(payload.get('status')=='completed_chunk','chunk status must be completed_chunk')
    check(payload.get('formal_baseline')=='Q1-Q1953','formal baseline mismatch')
    check(payload.get('production_write') is False,'production_write must be false')
    check(payload.get('db_write') is False,'db_write must be false')
    drafts=payload.get('drafts',[])
    check(isinstance(drafts,list) and len(drafts)==EXPECTED_SIZES[chunk_no],f'chunk size mismatch: {len(drafts) if isinstance(drafts,list) else "non-list"}')
    if not isinstance(drafts,list): drafts=[]
    check(len({str(x.get('draft_id')) for x in drafts if isinstance(x,dict)})==len(drafts),'duplicate/non-object drafts')
    stems={}
    for d in drafts:
        if not isinstance(d,dict): errors.append('non-object draft'); continue
        did=str(d.get('draft_id') or '?'); p=f'{did}: '
        check(d.get('status')=='accepted',p+'status must be accepted')
        check(not FORBIDDEN.intersection(d),p+'formal Q ID allocation forbidden')
        check(d.get('source')=='original',p+'source must be original')
        task=str(d.get('proposed_task') or ''); ability=str(d.get('primary_ability') or '')
        check(task in TASK_PRIMARY and TASK_PRIMARY.get(task)==ability,p+'task/primary mismatch')
        check(d.get('level') in {1,2,3,4},p+'invalid level')
        safety=str(d.get('safety') or '')
        check(safety in {'none','moderate','critical'},p+'invalid safety')
        if task=='safety_priority': check(safety in {'moderate','critical'},p+'safety_priority cannot have safety none')
        stem=str(d.get('question_text') or '')
        check(bool(stem.strip()),p+'question text required')
        check(len(stem)<=400,p+'stem exceeds 400 chars')
        if len(stem)>300: check(bool(str(d.get('length_exception_reason') or '').strip()),p+'stem >300 needs exception reason')
        stems[did]=norm(stem)
        choices=d.get('choices',{}); reasons=d.get('choice_explanations',{})
        choice_ok=isinstance(choices,dict) and isinstance(reasons,dict) and set(choices)==set(reasons)==set('12345')
        check(choice_ok,p+'five choices/explanations required')
        if choice_ok:
            check(all(isinstance(v,str) and v.strip() for v in [*choices.values(),*reasons.values()]),p+'blank choice/explanation')
            check(len({norm(v) for v in choices.values()})==5,p+'duplicate choice text')
        ans=d.get('correct_choices',[])
        check(isinstance(ans,list) and len(ans)==1 and str(ans[0]) in '12345',p+'single best answer required')
        check(bool(str(d.get('explanation') or '').strip()),p+'explanation required')
        evidence=d.get('evidence',[])
        check(isinstance(evidence,list) and bool(evidence),p+'evidence required')
        if isinstance(evidence,list):
            check(all(isinstance(e,dict) and str(e.get('url','')).startswith('https://') and bool(str(e.get('support','')).strip()) for e in evidence),p+'invalid evidence')
        review=d.get('semantic_review',{})
        check(isinstance(review,dict) and review.get('decision')=='accepted',p+'semantic review must be accepted')
        if isinstance(review,dict):
            for key in ('candidate_demand','why_not_same_demand','reviewer','reviewed_on'):
                check(bool(str(review.get(key,'')).strip()),p+f'semantic review missing {key}')
            check(review.get('expert_signoff') is False,p+'human expert signoff must not be fabricated')
        check(d.get('expert_signoff') is False,p+'draft expert_signoff must remain false')
        slot=str(d.get('slot_type') or '')
        if slot in {'singleton_second','multi_reinforcement'}:
            check(bool(str(d.get('target_node_id') or '').strip()),p+'existing Node target required')
            check(bool(d.get('reference_question_ids')),p+'formal refs required')
            existing={(str(x.get('task')),str(x.get('primary_ability'))) for x in d.get('existing_demands',[]) if isinstance(x,dict)}
            check((task,ability) not in existing,p+'candidate metadata demand duplicates existing demand')
        elif slot=='new_node':
            check(d.get('target_node_id') is None,p+'new Node ID must remain unallocated')
            check(d.get('reference_question_ids')==[],p+'new Node cannot claim formal refs')
            check(bool(str(d.get('target_node_label') or '').strip()),p+'new Node label required')
            collision=d.get('new_node_collision_review',{})
            check(isinstance(collision,dict) and collision.get('decision')=='accepted_new_node',p+'accepted new-node collision review required')
        else: check(False,p+f'invalid slot {slot!r}')
    keys=list(stems)
    for i,left in enumerate(keys):
        for right in keys[i+1:]:
            if stems[left] and stems[left]==stems[right]: errors.append(f'exact duplicate stems inside chunk: {left},{right}')
    return {'hard_errors':errors,'warnings':warnings,'draft_count':len(drafts)}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('chunk',type=int,choices=range(1,7)); args=parser.parse_args()
    path=CHUNK_DIR/f'chunk_{args.chunk:02d}.json'; report=build_report(read(path),args.chunk)
    print(json.dumps(report,ensure_ascii=False,indent=2)); return 1 if report['hard_errors'] else 0
if __name__=='__main__': raise SystemExit(main())
