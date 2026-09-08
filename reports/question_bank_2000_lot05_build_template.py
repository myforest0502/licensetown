"""Build QID-free Lot05 authoring template from the reviewed assignment."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ASSIGN=ROOT/'reports'/'question_bank_2000_lot05_assignment_reviewed_v01.json'
OUT=ROOT/'staging'/'question_bank_2000_lot05_template_v01.json'


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))

def main():
    assignment=read(ASSIGN)
    drafts=[]
    for row in assignment['assignments']:
        draft={
            'draft_id':row['draft_id'],
            'draft_order':row['draft_order'],
            'status':'authoring',
            'source':'original',
            'slot_type':row['slot_type'],
            'target_node_id':row.get('canonical_node_id'),
            'target_node_label':row.get('label'),
            'reference_question_ids':row.get('question_ids',[]),
            'existing_demands':row.get('existing_demands',[]),
            'proposed_category_small':row['category_small'],
            'proposed_task':row['proposed_task'],
            'primary_ability':row['primary_ability'],
            'secondary_ability':None,
            'level':row['level'],
            'safety':'none',
            'title':'',
            'question_text':'',
            'choices':{str(i):'' for i in range(1,6)},
            'correct_choices':[],
            'explanation':'',
            'choice_explanations':{str(i):'' for i in range(1,6)},
            'evidence':[],
            'semantic_review':'pending',
            'expert_signoff':False,
        }
        if row['slot_type']=='new_node':
            draft['target_node_id']=None
            draft['reference_question_ids']=[]
            draft['target_node_label']=''
            draft['new_node_collision_review']='pending'
        drafts.append(draft)
    if len(drafts)!=41: raise ValueError(len(drafts))
    payload={
        'lot':5,
        'formal_baseline':assignment['formal_baseline'],
        'status':'template_only',
        'q_ids_reserved':False,
        'production_write':False,
        'db_write':False,
        'quotas':{
            'task':assignment['task_quota'],
            'level':assignment['level_quota'],
            'safety_moderate_or_critical':assignment['required_safety_augment'],
            'minimum_strong_formations':assignment['required_strong_formations'],
            'slot_type':{'singleton_second':18,'multi_reinforcement':20,'new_node':3},
        },
        'drafts':drafts,
        'guardrails':[
            'No formal Q IDs or Knowledge Node IDs are allocated in this template.',
            'Each existing-Node draft must add a genuinely different semantic demand.',
            'New-node drafts require collision review before allocation.',
            'Final task, level, safety, category and slot quotas must remain exact.',
        ],
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'drafts':len(drafts),'output':str(OUT)},ensure_ascii=False))
    return 0

if __name__=='__main__': raise SystemExit(main())
