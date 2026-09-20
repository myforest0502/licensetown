"""Opt-in PT strategy adapter. Existing selector remains Q-selection authority."""
from collections import defaultdict
from datetime import datetime, timezone

VERSION = 'learning_strategy_runtime_pilot_v0.1'
EXPLORATION_FLOOR = 5
METADATA_KEYS = ('strategy_version','strategy_recommended_field','strategy_learning_intent',
                 'strategy_priority_score','strategy_reason_codes','strategy_priority_components',
                 'strategy_shadow_or_authority','strategy_fallback_reason',
                 'learning_lifecycle_version','learning_lifecycle_phase',
                 'learning_lifecycle_coverage_checkpoint','learning_lifecycle_repair_priority',
                 'learning_lifecycle_retention_priority','learning_lifecycle_reason_codes',
                 'learning_lifecycle_missing_evidence')


def pilot_enabled(enabled, user_id, pilot_ids):
    return bool(enabled and user_id and user_id in pilot_ids)


def _lifecycle_metadata(strategy):
    lifecycle = strategy.get('learning_lifecycle')
    if not isinstance(lifecycle, dict):
        return {}
    return {
        'learning_lifecycle_version': lifecycle.get('version'),
        'learning_lifecycle_phase': lifecycle.get('phase'),
        'learning_lifecycle_coverage_checkpoint': lifecycle.get('coverage_checkpoint_reached'),
        'learning_lifecycle_repair_priority': lifecycle.get('repair_priority'),
        'learning_lifecycle_retention_priority': lifecycle.get('retention_priority'),
        'learning_lifecycle_reason_codes': lifecycle.get('reason_codes', []),
        'learning_lifecycle_missing_evidence': lifecycle.get('missing_evidence', []),
    }


def _time(value):
    if isinstance(value,str):
        value=datetime.fromisoformat(value.replace('Z','+00:00'))
    if not isinstance(value,datetime):
        raise ValueError('Observed timestamp required')
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def completion_context(events, as_of):
    """Consecutive completed work, never goals or additional weakness blocks.

    Web plans use verified ten-answer web sessions. Completed pilot LINE sessions
    are explicit thirty-answer groups with consistent strategy metadata. Partial
    pilot sessions fail closed until finished (no zero-completion assumption).
    """
    from question_bank import CATEGORY_NAMES,get_category_small
    from learning_strategy_context_shadow import derive_recommendation_plan_context
    names={v:k for k,v in CATEGORY_NAMES.items()}
    plans,web,pilot=[],defaultdict(list),defaultdict(list)
    for e in events:
        at=_time(e['answered_at'])
        if at>=as_of:
            continue
        payload=e.get('question_results')
        if e.get('mode')=='recommendation_plan' and isinstance(payload,dict):
            plans.append({'at':at,'field_id':names[payload['field']],
                          'completed_recommendation_questions':0})
        key=str(e.get('event_key',''))
        if not isinstance(payload,list):
            continue
        if key.startswith('web-recommendation:') and key.rsplit(':',1)[-1].isdigit():
            web[key.rsplit(':',1)[0]].append((at,int(key.rsplit(':',1)[-1]),len(payload)))
        if any(r.get('strategy_version')==VERSION and r.get('strategy_shadow_or_authority')=='soft_pilot' for r in payload):
            pilot[key.rsplit(':',1)[0]].extend((at,r) for r in payload)
    plans.sort(key=lambda p:p['at'])
    for rows in web.values():
        if len(rows)!=10 or {r[1] for r in rows}!=set(range(1,11)) or sum(r[2] for r in rows)!=10:
            continue
        start,end=min(r[0] for r in rows),max(r[0] for r in rows)
        prior=[p for p in plans if p['at']<start]
        if prior:
            p=prior[-1]
            next_at=next((n['at'] for n in plans if n['at']>p['at']),as_of)
            if end<next_at:
                p['completed_recommendation_questions']+=10
    for rows in pilot.values():
        fields={r.get('strategy_recommended_field') for _,r in rows}
        if len(rows)!=30 or len(fields)!=1 or len({r.get('question_id') for _,r in rows})!=30:
            raise ValueError('Incomplete pilot completion context')
        field=fields.pop()
        plans.append({'at':max(at for at,_ in rows),'field_id':field,
                      'completed_recommendation_questions':sum(
                          get_category_small(r['question_id'])==field for _,r in rows)})
    if not plans:
        raise ValueError('Recommendation completion context unavailable')
    plans.sort(key=lambda p:p['at'])
    row=derive_recommendation_plan_context(plans)['rows'][-1]
    return {f:{'consecutive_field_blocks':row['completed_30q_equivalent_after'] if f==row['field_id'] else 0}
            for f in range(1,19)}


def strategy_snapshot(attempts, events, as_of):
    from adaptive_question_selector import _node_attempt_summary,_priority
    from knowledge_node_state_transition import derive_all_user_node_states
    from question_bank import question_ids,get_question_tag,get_category_small
    from question_equivalence import canonicalize_question_evidence_node
    from field_evidence import build_field_evidence
    from field_progress import build_field_progress
    from field_learning_target_shadow import build_field_targets
    from learning_lifecycle import build_learning_lifecycle
    from learning_strategy_shadow import build_learning_strategy
    contexts=completion_context(events,as_of)
    state_rows=derive_all_user_node_states(attempts,as_of=as_of)
    states={r['canonical_node_id']:r['state'] for r in state_rows}
    summaries=_node_attempt_summary(attempts)
    critical=defaultdict(set)
    for q in question_ids():
        tag=get_question_tag(q)
        node=canonicalize_question_evidence_node(q,tag['knowledge_node_id'])
        if tag.get('safety')=='critical' and node in summaries:
            if _priority(states[node],summaries[node],'critical')[1] in {'safety_wrong','safety_unresolved'}:
                critical[get_category_small(q)].add(node)
    last={}
    for a in attempts:
        f=get_category_small(a['question_id'])
        at=_time(a['answered_at'])
        last[f]=max(at,last.get(f,at))
    for f,c in contexts.items():
        c['critical_safety_unresolved_count']=len(critical[f])
        if f in last:
            c['days_since_last_field_study']=max(0,(as_of-last[f]).total_seconds()/86400)
    evidence=build_field_evidence(attempts,as_of=as_of)
    progress=build_field_progress(evidence)
    targets=build_field_targets(evidence,progress,context_by_field=contexts)
    critical_nodes=set().union(*critical.values()) if critical else set()
    lifecycle=build_learning_lifecycle(
        evidence, targets, state_rows,
        critical_safety_unresolved_count=len(critical_nodes),
    )
    strategy=build_learning_strategy(evidence,progress,context_by_field=contexts)
    strategy['learning_lifecycle']=lifecycle
    return strategy


def refine_session(attempts, baseline, audit, events, *, exclude_ids=(), as_of=None):
    """Protect Safety/due and the five-slot exploration floor; soft-target the rest.

    Stage E may reroute to the next ranked field when the top field cannot fill
    the currently replaceable slots without weakening repeat/Safety guards.
    Caller must gate before loading events or importing this adapter. This
    function never reads/writes DB, changes flags, or grants the pure engine
    question-selection authority. Exceptions leave caller's baseline intact.
    """
    from adaptive_question_selector import select_node_adaptive_questions,_field_node_coverage
    from short_term_repeat_guard import blocked_short_term_evidence_ids
    from question_bank import question_ids,get_category_small,get_question_tag,get_quiz_question
    from question_equivalence import canonicalize_question_evidence_id as eq
    if len(baseline)!=30:
        return baseline
    as_of=as_of or datetime.now(timezone.utc)
    strategy=strategy_snapshot(attempts,events,as_of)
    field=strategy['recommended_field_id']
    meta={'strategy_version':VERSION,'strategy_recommended_field':field,
          'strategy_learning_intent':strategy['learning_intent'],
          'strategy_priority_score':strategy['priority_score'],
          'strategy_reason_codes':strategy['reason_codes'],
          'strategy_priority_components':strategy['priority_components']}
    meta.update(_lifecycle_metadata(strategy))
    def fallback(reason):
        for q in baseline:
            audit.setdefault(q['id'],{}).update(meta,strategy_shadow_or_authority='fallback',strategy_fallback_reason=reason)
        return baseline
    if not field:
        return fallback('no_strategy_candidate')

    ranked=list(strategy.get('ranked_fields') or ())
    protected=[]
    exploration_kept=0
    for q in baseline:
        row=audit.get(q['id'],{})
        is_exploration=row.get('selection_group')=='exploration'
        if is_exploration and not ranked:
            # Legacy/minimal snapshots cannot prove safe alternate field supply.
            keep_exploration=True
        else:
            keep_exploration=is_exploration and exploration_kept<EXPLORATION_FLOOR
            if keep_exploration:
                exploration_kept+=1
        if (keep_exploration
                or row.get('selection_reason') in {'safety_wrong','safety_unresolved','recheck_due'}
                or get_question_tag(q['id']).get('safety') in {'critical','high','moderate'}):
            protected.append(q)
    needed=30-len(protected)
    if not needed:
        return fallback('no_unprotected_slots')

    protected_ids={eq(q['id']) for q in protected}
    blocked=blocked_short_term_evidence_ids(attempts,as_of=as_of)|{eq(q) for q in exclude_ids}
    recent={eq(a['question_id']) for a in sorted(attempts,key=lambda a:_time(a['answered_at']),reverse=True)[:30]}
    field_map,_=_field_node_coverage(attempts)

    if ranked:
        candidates=[row for row in ranked if row.get('allocation_candidate',True)
                    and row.get('priority_score',0)>0 and row.get('field_id')]
    else:
        candidates=[{'field_id':field,'learning_intent':strategy['learning_intent'],
                     'priority_score':strategy['priority_score'],'reason_codes':strategy['reason_codes'],
                     'priority_components':strategy['priority_components']}]

    chosen_candidate=None
    preferred=None
    had_coarse_supply=False
    intent_map={'coverage':'exploration','repair':'repair','safety_review':'repair',
                'retention':'recheck','maintenance':'recheck','attainment':'repair'}
    for candidate in candidates:
        candidate_field=candidate['field_id']
        eligible={eq(q) for q in question_ids()
                  if field_map.get(eq(q),get_category_small(q))==candidate_field}-blocked-recent-protected_ids
        if len(eligible)<needed:
            continue
        had_coarse_supply=True
        intent=intent_map.get(candidate.get('learning_intent'))
        selected=select_node_adaptive_questions(
            attempts,needed,exclude_ids=blocked|recent|protected_ids,
            category_small=candidate_field,learning_intent=intent,as_of=as_of)
        if len(selected)<needed:
            continue
        chosen_candidate=candidate
        preferred=selected
        break

    if chosen_candidate is None:
        return fallback('selector_supply_insufficient' if had_coarse_supply else 'eligible_supply_insufficient')

    field=chosen_candidate['field_id']
    reasons=list(chosen_candidate.get('reason_codes') or ())
    if field!=strategy['recommended_field_id']:
        reasons.append('eligible_supply_reroute')
    meta={'strategy_version':VERSION,'strategy_recommended_field':field,
          'strategy_learning_intent':chosen_candidate.get('learning_intent'),
          'strategy_priority_score':chosen_candidate.get('priority_score',0.0),
          'strategy_reason_codes':reasons,
          'strategy_priority_components':chosen_candidate.get('priority_components') or {}}
    meta.update(_lifecycle_metadata(strategy))

    chosen=list(protected)
    seen={eq(q['id']) for q in chosen}
    records={r['question_id']:r for r in preferred}
    for r in preferred:
        if len(chosen)==30:
            break
        if eq(r['question_id']) not in seen:
            chosen.append(get_quiz_question(r['question_id']))
            seen.add(eq(r['question_id']))
    if len(chosen)!=30 or any(eq(q['id']) in blocked|recent for q in chosen):
        return fallback('guard_or_protected_slot_conflict')
    protected_qids={q['id'] for q in protected}
    updated={}
    for q in chosen:
        qid=q['id']
        row=dict(audit.get(qid,{}))
        if qid not in protected_qids:
            r=records[qid]
            row.update(selection_reason=r['priority_reason'],selection_group=r['priority_group'],
                       selection_score=r['priority_score'],repair_evidence_quality=r['repair_evidence_quality'],
                       recent_question_repeat=False,recent_cooldown_bypassed=False)
        row.update(meta,strategy_shadow_or_authority='soft_pilot',strategy_fallback_reason=None)
        updated[qid]=row
    audit.clear()
    audit.update(updated)
    return chosen
