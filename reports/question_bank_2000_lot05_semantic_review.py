"""Apply reviewed Lot05 target/task overrides before question authoring.

This keeps the deterministic raw roster immutable as an audit trail while producing a
medically more natural authoring plan. No formal Question Bank write occurs here.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGETS=ROOT/'reports'/'question_bank_2000_lot05_targets_v01.json'
ASSIGN=ROOT/'reports'/'question_bank_2000_lot05_assignment_v01.json'
ALT=ROOT/'reports'/'question_bank_2000_lot05_c7_alternatives.json'
OUT_T=ROOT/'reports'/'question_bank_2000_lot05_targets_reviewed_v01.json'
OUT_A=ROOT/'reports'/'question_bank_2000_lot05_assignment_reviewed_v01.json'

ABILITY={
 'assessment_selection':'MEASURE','device_selection':'PRESCRIBE','fact_recall':'KNOW',
 'finding_interpretation':'INTERPRET','functional_goal_decision':'DECIDE',
 'intervention_selection':'PRESCRIBE','prognosis_prediction':'PREDICT','safety_priority':'DECIDE',
}

# Pairwise swaps preserve exact global task quotas while removing semantically weak
# machine assignments.
TASK_OVERRIDES={
 'L05-C1-S01':'assessment_selection',
 'L05-C18-M01':'intervention_selection',
 'L05-C2-S03':'finding_interpretation',
 'L05-C15-M02':'functional_goal_decision',
 'L05-C8-S02':'assessment_selection',
 'L05-C14-S01':'intervention_selection',
 'L05-C8-M03':'safety_priority',
 'L05-C15-S01':'finding_interpretation',
 'L05-C11-S01':'device_selection',
 'L05-C2-N01':'prognosis_prediction',
 # A new anatomy Node should test anatomy/clinical interpretation rather than a
 # forced functional-goal judgment. Down-syndrome mobility is a natural place for
 # the corresponding functional-goal demand, so this pair preserves the quota.
 'L05-C1-N01':'finding_interpretation',
 'L05-C4-S01':'functional_goal_decision',
}

# Machine-selected C7 singleton was an exam-answer bookkeeping artifact rather than
# a useful medical Knowledge Node. Replace it with an untouched burn-depth Node.
REPLACE_DRAFT='L05-C7-S01'
REPLACEMENT_NODE='KN0690'


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))

def main():
    targets=read(TARGETS)
    assignment=read(ASSIGN)
    alternatives=read(ALT)
    replacement=next(x for x in alternatives if x['knowledge_node_id']==REPLACEMENT_NODE)

    reviewed_targets=json.loads(json.dumps(targets,ensure_ascii=False))
    target_row=next(x for x in reviewed_targets['existing_node_targets'] if x['lot_target_id']==REPLACE_DRAFT)
    target_row.update({
        'canonical_node_id':replacement['knowledge_node_id'],
        'label':replacement['label'],
        'question_ids':[replacement['question_id']],
        'existing_demands':[{'task':replacement['task'],'primary_ability':replacement['primary_ability']}],
        'sources':{replacement['source']:1},
        'levels':[replacement['level']],
        'safety':[replacement['safety']],
        'review_replacement_reason':'Removed non-medical exam-answer bookkeeping Node; burn-depth Node supports a distinct safety demand.',
    })
    reviewed_targets['status']='reviewed_target_roster'
    reviewed_targets['review_overrides']={REPLACE_DRAFT:REPLACEMENT_NODE}

    reviewed=json.loads(json.dumps(assignment,ensure_ascii=False))
    row=next(x for x in reviewed['assignments'] if x['draft_id']==REPLACE_DRAFT)
    row.update({
        'canonical_node_id':replacement['knowledge_node_id'],
        'label':replacement['label'],
        'question_ids':[replacement['question_id']],
        'existing_demands':[{'task':replacement['task'],'primary_ability':replacement['primary_ability']}],
        'sources':{replacement['source']:1},
        'levels':[replacement['level']],
        'safety':[replacement['safety']],
        'review_replacement_reason':'Removed non-medical exam-answer bookkeeping Node.',
    })

    for item in reviewed['assignments']:
        task=TASK_OVERRIDES.get(item['draft_id'], item['proposed_task'])
        item['proposed_task']=task
        item['primary_ability']=ABILITY[task]
        if item['draft_id']==REPLACE_DRAFT:
            item['proposed_task']='safety_priority'; item['primary_ability']='DECIDE'; item['level']=4

    expected_tasks=Counter({k:int(v) for k,v in reviewed['task_quota'].items()})
    actual_tasks=Counter(x['proposed_task'] for x in reviewed['assignments'])
    if actual_tasks!=expected_tasks:
        raise ValueError(f'task quota changed by semantic review: {actual_tasks} != {expected_tasks}')
    expected_levels=Counter({str(k):int(v) for k,v in reviewed['level_quota'].items()})
    actual_levels=Counter(str(x['level']) for x in reviewed['assignments'])
    if actual_levels!=expected_levels:
        raise ValueError(f'level quota changed by semantic review: {actual_levels} != {expected_levels}')
    for item in reviewed['assignments']:
        if item['slot_type']=='new_node': continue
        existing={(x['task'],x['primary_ability']) for x in item.get('existing_demands',[])}
        demand=(item['proposed_task'],item['primary_ability'])
        if demand in existing:
            raise ValueError(f"{item['draft_id']}: reviewed task duplicates existing demand {demand}")

    reviewed['status']='semantic_reviewed_assignment'
    reviewed['semantic_overrides']=TASK_OVERRIDES
    reviewed['target_replacement']={REPLACE_DRAFT:REPLACEMENT_NODE}
    reviewed['review_notes']=[
        'Task swaps preserve the exact 41-question task quota.',
        'The C7 bookkeeping artifact target was replaced before authoring.',
        'New-node concepts are still pending collision review and may drive further task swaps if required.',
    ]
    OUT_T.write_text(json.dumps(reviewed_targets,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    OUT_A.write_text(json.dumps(reviewed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tasks':dict(actual_tasks),'levels':dict(actual_levels),'replacement':REPLACEMENT_NODE},ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
