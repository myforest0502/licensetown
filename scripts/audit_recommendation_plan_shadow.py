"""Offline plan-time replay, using anonymous exports and unchanged formal logic."""
import argparse
import json
from pathlib import Path

from scripts.audit_learning_strategy_shadow import (
    _evidence_builder, _time, normalize, safety_context, eligible_supply,
)


def replay_plans(data):
    from question_bank import CATEGORY_NAMES, get_category_small
    from field_progress import build_field_progress
    from learning_strategy_shadow import build_learning_strategy
    from learning_strategy_context_shadow import derive_recommendation_plan_context
    attempts = normalize(data['attempts'])
    names = {v:k for k,v in CATEGORY_NAMES.items()}
    plans = sorted(data['plans'],key=lambda p:_time(p['answered_at']))
    if len({_time(p['answered_at']) for p in plans}) != len(plans) or not plans:
        raise ValueError('Unique plan timestamps required')
    sessions = data['sessions']
    if len({(s['started_at'],s['completed_at']) for s in sessions}) != len(sessions):
        raise ValueError('Duplicate session observations')
    observations = []
    for i,p in enumerate(plans):
        at = _time(p['answered_at'])
        end = _time(plans[i+1]['answered_at']) if i+1<len(plans) else attempts[-1]['answered_at']
        completed = 0
        for s in sessions:
            # Export contains only explicit web-recommendation answer events.
            # Require a complete contiguous ten-answer session, never plan goal.
            valid = int(s['answer_events']) == int(s['answered_count']) == int(s['max_position']) == 10 and int(s['min_position']) == 1
            if valid and at < _time(s['started_at']) <= _time(s['completed_at']) <= end:
                completed += 10
        observations.append({'field_id':names[p['field']], 'goal':int(p['goal']),
                             'completed_recommendation_questions':completed})
    derived = derive_recommendation_plan_context(observations)
    build_evidence = _evidence_builder()
    output, previous = [], {}
    for i,(p,c) in enumerate(zip(plans,derived['rows'])):
        at = _time(p['answered_at'])
        prefix = [a for a in attempts if a['answered_at'] < at]
        evidence = build_evidence(prefix,as_of=at)
        progress = build_field_progress(evidence)
        safety = safety_context(prefix,at)
        last = {get_category_small(a['question_id']):a['answered_at'] for a in prefix}
        contexts = {f:{'critical_safety_unresolved_count':safety[f],**previous.get(f,{})} for f in range(1,19)}
        for f in last:
            contexts[f]['days_since_last_field_study'] = (at-last[f]).total_seconds()/86400
        # #349 context describes the observed actual-plan field, not an invented
        # streak following Shadow. Other field concentration remains unavailable.
        contexts[c['field_id']]['consecutive_field_blocks'] = c['consecutive_field_blocks']
        strategy = build_learning_strategy(evidence,progress,context_by_field=contexts)
        ranked = strategy['ranked_fields']
        top = ranked[0]
        actual = next(r for r in ranked if r['field_id']==c['field_id'])
        # Same evidence with concentration omitted isolates the arithmetic effect.
        without = {f:{k:v for k,v in ctx.items() if k!='consecutive_field_blocks'} for f,ctx in contexts.items()}
        baseline = build_learning_strategy(evidence,progress,context_by_field=without)
        before = next(r for r in baseline['ranked_fields'] if r['field_id']==c['field_id'])
        output.append({'plan_index':i+1,'timestamp':at.isoformat(),'attempt_prefix_count':len(prefix),
            'actual_plan_field':CATEGORY_NAMES[c['field_id']], 'actual_goal':c['goal'],
            'actual_reason_code':p.get('reason_code') if p.get('reason_code') in {'confident_wrong_repair','safety_repair'} else None,
            'actual_learning_intent':p.get('learning_intent') if p.get('learning_intent') in {'repair','recheck','exploration'} else None,
            'completed_recommendation_questions_after_plan':c['completed_recommendation_questions'],
            'consecutive_field_blocks_at_plan_time':c['consecutive_field_blocks'],
            'shadow_top1_field':top['field_name'],'shadow_top3_fields':[r['field_name'] for r in ranked[:3]],
            'shadow_learning_intent':top['learning_intent'],'shadow_priority_score':top['priority_score'],
            'shadow_reason_codes':top['reason_codes'],'shadow_priority_components':top['priority_components'],
            'top1_match':top['field_id']==c['field_id'],'top3_match':c['field_id'] in [r['field_id'] for r in ranked[:3]],
            'concentration_penalty':top['priority_components']['concentration_penalty'],
            'actual_field_concentration_penalty':actual['priority_components']['concentration_penalty'],
            'actual_field_score_reduction':before['priority_score']-actual['priority_score'],
            'critical_safety_unresolved_count':top['target']['critical_safety_unresolved_count'],
            'safety_contradiction':bool(any(safety.values()) and top['learning_intent']!='safety_review'),
            'unavailable':['additional_blocks_completed','days_to_exam','other_field_concentration'],
            **eligible_supply(prefix,top['field_id'],at)})
        previous = {p['field_id']:{'previous_progress_score':p['field_progress_score'],
                    'previous_stable_ratio':p['state_counts']['stable']/max(1,p['touched_canonical_nodes'])} for p in progress['fields']}
    final_evidence = build_evidence(attempts,as_of=attempts[-1]['answered_at'])
    final = build_learning_strategy(final_evidence,build_field_progress(final_evidence))
    small = [{'field':r['field_name'],'supply':r['target']['total_question_count'],
              'answers':r['target']['evaluation']['evaluable_answer_count'],'raw_state':r['field_state']}
             for r in final['ranked_fields'] if r['field_id'] in (3,11)]
    return {'shadow_only':True,'selection_authority':False,'attempt_count':len(attempts),
            'plan_count':len(output),'context':derived,'plans':output,'small_bank':small,
            'summary':{'top1_matches':sum(r['top1_match'] for r in output),
                       'top3_matches':sum(r['top3_match'] for r in output),
                       'safety_contradictions':sum(r['safety_contradiction'] for r in output),
                       'supply_insufficient':sum(r['eligible_supply_insufficient'] for r in output)}}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    result=replay_plans(json.loads(args.input.read_text(encoding='utf-8')))
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result['summary']))
