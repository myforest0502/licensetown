"""Build the structural authoring template for Question Bank 2000 production Lot04."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGETS=ROOT/'reports'/'question_bank_2000_lot04_targets_v01.json'
OUT=ROOT/'staging'/'question_bank_2000_lot04_template_v01.json'
TASK_QUOTA={'assessment_selection':9,'device_selection':2,'fact_recall':2,'finding_interpretation':14,'functional_goal_decision':4,'intervention_selection':8,'prognosis_prediction':3,'safety_priority':6}
LEVEL_QUOTA={'1':2,'2':16,'3':20,'4':10}
CATEGORY_QUOTA={'1':4,'2':5,'3':2,'4':2,'5':2,'6':3,'7':3,'8':6,'9':2,'10':2,'11':3,'12':2,'13':3,'14':2,'15':4,'17':1,'18':2}
def blank_content():
    return {'title':'','question_text':'','choices':{'1':'','2':'','3':'','4':'','5':''},'correct_choices':[],'explanation':'','choice_explanations':{'1':'','2':'','3':'','4':'','5':''},'proposed_task':'','primary_ability':'','secondary_ability':None,'level':None,'safety':'none','clinical_intent':'','semantic_review':{'reference_demand':'','candidate_demand':'','why_not_same_demand':'','related_formal_questions':[],'decision':'pending','reviewer':'','reviewed_on':'','expert_signoff':False},'evidence':[],'reviewed_sha256':''}
def main():
    roster=json.loads(TARGETS.read_text(encoding='utf-8'))
    if roster.get('formal_baseline')!='Q1-Q1905': raise ValueError('Lot04 baseline must be Q1-Q1905')
    drafts=[]
    for t in roster['existing_node_targets']:
        drafts.append({'draft_id':t['lot_target_id'],'status':'authoring','slot_type':t['slot_type'],'target_node_id':t['canonical_node_id'],'target_node_label':t['label'],'reference_question_ids':t['question_ids'],'existing_demands':t['existing_demands'],'proposed_category_small':t['category_small'],'source':'original','required_new_demand_outside_existing':True,**blank_content()})
    for r in roster['new_node_reservations']:
        c=int(r['category_small'])
        for i in range(1,int(r.get('count',1))+1):
            drafts.append({'draft_id':f'L04-C{c}-N{i:02d}','status':'authoring','slot_type':'new_node','target_node_id':None,'target_node_label':'','reference_question_ids':[],'existing_demands':[],'proposed_category_small':c,'source':'original','required_new_demand_outside_existing':False,'new_node_created_only_at_formal_integration':True,**blank_content()})
    if len(drafts)!=48 or len({d['draft_id'] for d in drafts})!=48: raise ValueError('Lot04 template must contain 48 unique drafts')
    payload={'batch':'question_bank_2000_production_lot04_v01','status':'template_only','formal_baseline':'Q1-Q1905','q_ids_reserved':False,'production_write':False,'db_write':False,'accepted_target_count':48,'quotas':{'category':CATEGORY_QUOTA,'task':TASK_QUOTA,'level':LEVEL_QUOTA,'slot_type':{'singleton_second':27,'multi_reinforcement':17,'new_node':4},'minimum_strong_formations':37,'safety_moderate_or_critical':12},'drafts':drafts,'authoring_rules':['Do not allocate formal Q IDs in staging.','Each existing-Node draft must add a genuinely different semantic demand.','All five choices and all five choice explanations are required.','Stem <=300 Japanese characters unless clinically necessary and <=400.','New-Node slots require semantic search against formal Q1-Q1905.','Every accepted draft requires evidence and completed semantic_review before sealing.','AI review must keep expert_signoff=false unless a real human expert signs off.']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print({'drafts':48,'existing':44,'new_node':4}); return 0
if __name__=='__main__': raise SystemExit(main())
