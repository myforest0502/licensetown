"""Opt-in PT strategy adapter. Existing selector remains Q-selection authority."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

VERSION = 'learning_strategy_runtime_pilot_v0.1'
FLOOR_UP_VERSION = 'daily_floor_up_v0.1'
TOKYO = ZoneInfo('Asia/Tokyo')
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


def trusted_strategy_evidence_attempts(attempts):
    """Keep editorially trusted evidence for strategy/readiness decisions.

    provisional_bulk remains usable for practice/repeat guards and Safety, but
    ordinary provisional answers must not dominate weakness/readiness routing.
    """
    from question_bank import QuestionBankError, get_question_tag

    kept = []
    excluded = 0
    for item in attempts:
        question_id = str(item.get("question_id") or "")
        try:
            tag = get_question_tag(question_id)
        except (QuestionBankError, KeyError, TypeError, ValueError):
            kept.append(item)
            continue
        provisional = str(tag.get("tag_status") or "") == "provisional_bulk"
        safety = str(tag.get("safety") or "none")
        if provisional and safety not in {"critical", "high", "moderate"}:
            excluded += 1
            continue
        kept.append(item)
    return kept, excluded


# Backward-compatible internal alias for existing tests/callers.
_strategy_evidence_attempts = trusted_strategy_evidence_attempts


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
    from question_bank import CATEGORY_NAMES,QuestionBankError,get_category_small
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
        question_ids={r.get('question_id') for _,r in rows}
        if (len(rows)!=30 or len(fields)!=1 or len(question_ids)!=30
                or None in question_ids):
            continue
        field=fields.pop()
        if field not in range(1,19):
            continue
        try:
            completed_questions=sum(
                get_category_small(r['question_id'])==field for _,r in rows)
        except (KeyError, TypeError, ValueError, QuestionBankError):
            continue
        plans.append({'at':max(at for at,_ in rows),'field_id':field,
                      'completed_recommendation_questions':completed_questions})
    if not plans:
        raise ValueError('Recommendation completion context unavailable')
    plans.sort(key=lambda p:p['at'])
    row=derive_recommendation_plan_context(plans)['rows'][-1]
    return {f:{'consecutive_field_blocks':row['completed_30q_equivalent_after'] if f==row['field_id'] else 0}
            for f in range(1,19)}


def strategy_snapshot(attempts, events, as_of, *, days_to_exam=None):
    from adaptive_question_selector import _node_attempt_summary,_priority
    from knowledge_node_state_transition import derive_all_user_node_states
    from question_bank import question_ids,get_question_tag,get_category_small
    from question_equivalence import canonicalize_question_evidence_node
    from field_evidence import build_field_evidence
    from field_progress import build_field_progress
    from field_learning_target_shadow import build_field_targets
    from licensetown.pt.learning_lifecycle import build_learning_lifecycle
    from learning_strategy_shadow import build_learning_strategy
    contexts=completion_context(events,as_of)
    strategy_attempts, excluded_provisional = trusted_strategy_evidence_attempts(attempts)
    state_rows=derive_all_user_node_states(strategy_attempts,as_of=as_of)
    states={r['canonical_node_id']:r['state'] for r in state_rows}
    summaries=_node_attempt_summary(strategy_attempts)
    critical=defaultdict(set)
    for q in question_ids():
        tag=get_question_tag(q)
        node=canonicalize_question_evidence_node(q,tag['knowledge_node_id'])
        if tag.get('safety')=='critical' and node in summaries:
            if _priority(states[node],summaries[node],'critical')[1] in {'safety_wrong','safety_unresolved'}:
                critical[get_category_small(q)].add(node)
    last={}
    for a in strategy_attempts:
        f=get_category_small(a['question_id'])
        at=_time(a['answered_at'])
        last[f]=max(at,last.get(f,at))
    for f,c in contexts.items():
        c['critical_safety_unresolved_count']=len(critical[f])
        if f in last:
            c['days_since_last_field_study']=max(0,(as_of-last[f]).total_seconds()/86400)
    evidence=build_field_evidence(
        strategy_attempts,
        as_of=as_of,
        node_states=state_rows,
    )
    progress=build_field_progress(evidence)
    targets=build_field_targets(evidence,progress,context_by_field=contexts)
    critical_nodes=set().union(*critical.values()) if critical else set()
    lifecycle=build_learning_lifecycle(
        evidence, targets, state_rows,
        critical_safety_unresolved_count=len(critical_nodes),
    )
    strategy=build_learning_strategy(
        evidence,
        progress,
        context_by_field=contexts,
        days_to_exam=days_to_exam,
        targets_bundle=targets,
    )
    strategy['editorial_evidence_policy']='exclude_general_provisional_bulk_keep_safety'
    strategy['excluded_provisional_general_attempt_count']=excluded_provisional
    strategy['learning_lifecycle']=lifecycle
    return strategy



def daily_floor_up_context(events, as_of):
    """Return today's completed 30q adaptive blocks and any persisted floor-up target.

    Floor-up is deliberately bounded to blocks 3 and 4 only. Blocks 1-2 and any
    work after block 4 stay on the ordinary LT strategy so one weak field cannot
    take over the whole learning day.
    """
    now = _time(as_of)
    today = now.astimezone(TOKYO).date()
    yesterday = today - timedelta(days=1)
    sessions = defaultdict(list)
    for event in events:
        payload = event.get('question_results')
        if not isinstance(payload, list):
            continue
        key = str(event.get('event_key') or '')
        if ':' not in key:
            continue
        root = key.rsplit(':', 1)[0]
        at = _time(event['answered_at'])
        for row in payload:
            if row.get('learning_source') == 'adaptive_daily':
                sessions[root].append((at, row))

    completed = []
    for root, rows in sessions.items():
        question_ids = {row.get('question_id') for _, row in rows}
        if len(rows) != 30 or len(question_ids) != 30 or None in question_ids:
            continue
        ended_at = max(at for at, _ in rows)
        day = ended_at.astimezone(TOKYO).date()
        targets = {
            int(row['floor_up_target_field'])
            for _, row in rows
            if row.get('floor_up_mode') == FLOOR_UP_VERSION
            and str(row.get('floor_up_target_field') or '').isdigit()
        }
        target = next(iter(targets)) if len(targets) == 1 else None
        completed.append({'root': root, 'day': day, 'ended_at': ended_at, 'floor_up_target': target})

    today_rows = sorted(
        (row for row in completed if row['day'] == today),
        key=lambda row: row['ended_at'],
    )
    today_target = next(
        (row['floor_up_target'] for row in today_rows if row['floor_up_target']),
        None,
    )
    yesterday_targets = [
        row['floor_up_target'] for row in completed
        if row['day'] == yesterday and row['floor_up_target']
    ]
    yesterday_target = yesterday_targets[-1] if yesterday_targets else None
    completed_blocks = len(today_rows)
    active = completed_blocks in {2, 3}
    return {
        'active': active,
        'completed_blocks_today': completed_blocks,
        'floor_up_day_block': completed_blocks - 1 if active else None,
        'today_target_field': today_target,
        'yesterday_target_field': yesterday_target,
    }



def _field_learning_progress_scores(attempts):
    """Reproduce the learner-facing field progress score used on the dashboard.

    The floor-up target must match what the learner can see: the lowest
    "分野別 学習進捗".  Use all formal attempts (not the stricter strategy-only
    evidence filter), because the dashboard presentation is built from the full
    learner history.  Accuracy is the all-time per-field question accuracy, while
    coverage and finish come from the formal Evidence -> Progress pipeline.
    """
    from field_evidence import build_field_evidence
    from field_progress import build_field_progress
    from licensetown.pt.learning_progress_presentation import calculate_learning_progress
    from question_bank import QuestionBankError, get_category_small

    evidence = build_field_evidence(attempts)
    progress = build_field_progress(evidence)
    accuracy_counts = defaultdict(lambda: [0, 0])
    for attempt in attempts:
        question_id = attempt.get('question_id')
        if not question_id:
            continue
        try:
            field_id = get_category_small(question_id)
        except (QuestionBankError, KeyError, TypeError, ValueError):
            continue
        accuracy_counts[field_id][0] += 1
        if attempt.get('is_correct') is True:
            accuracy_counts[field_id][1] += 1

    scores = {}
    for row in progress.get('fields') or ():
        field_id = int(row['field_id'])
        answered, correct = accuracy_counts[field_id]
        accuracy_percent = round(correct / answered * 100) if answered else None
        accuracy = (accuracy_percent / 100) if accuracy_percent is not None else None
        learning_progress = calculate_learning_progress(
            row.get('node_coverage'),
            accuracy,
            row.get('field_progress_score'),
        )
        display_percent = int(
            Decimal(str(learning_progress * 100)).quantize(
                Decimal('1'), rounding=ROUND_HALF_UP
            )
        )
        if learning_progress < 1.0:
            display_percent = min(display_percent, 99)
        scores[field_id] = {
            'learning_progress': learning_progress,
            'learning_progress_display_percent': display_percent,
            'coverage': row.get('node_coverage'),
            'accuracy': accuracy,
            'finish': row.get('field_progress_score'),
            'answered_count': answered,
        }
    return scores


def _floor_up_ranked_candidates(strategy, learning_progress_scores, yesterday_target=None):
    """Rank by the same learning-progress percentage shown to the learner.

    The lowest visible field progress is the primary and authoritative floor-up
    signal.  Accuracy, strict finish and unresolved repeated weakness only break
    ties.  The prior day's target may be moved back only when another field has
    the *same* learner-facing progress score; it must never displace a genuinely
    lower field.
    """
    rows = []
    for row in strategy.get('ranked_fields') or ():
        field_id = int(row.get('field_id') or 0)
        score = learning_progress_scores.get(field_id)
        if not field_id or not score:
            continue
        target = row.get('target') or {}
        evaluation = target.get('evaluation') or {}
        if not target.get('total_question_count'):
            continue
        rows.append((
            int(score.get('learning_progress_display_percent') or 0),
            float(score.get('learning_progress') or 0.0),
            float(score.get('accuracy') or 0.0),
            float(score.get('finish') or 0.0),
            -int(target.get('unresolved_repeated_weakness_node_count') or 0),
            field_id,
            row,
        ))
    rows.sort(key=lambda item: item[:6])

    # Rotation is allowed only inside the same percentage the learner actually sees.
    if yesterday_target and len(rows) > 1:
        minimum_display = rows[0][0]
        tied = [item for item in rows if item[0] == minimum_display]
        if len(tied) > 1:
            tied.sort(key=lambda item: (
                int(item[5]) == int(yesterday_target),
                item[1], item[2], item[3], item[4], item[5],
            ))
            rows = tied + [item for item in rows if item[0] != minimum_display]
    return [item[-1] for item in rows]

def _refine_floor_up_session(
    attempts, baseline, audit, strategy, events, *,
    exclude_ids=(), as_of=None,
):
    """Build one exact 30q field block for daily floor-up, or fail closed.

    A day gets at most two such blocks (61-90 and 91-120). The first block picks
    one low-floor field; the second reuses the same field for clean 30q analysis.
    Results remain ordinary formal attempts and therefore feed every existing LT
    state/progress/repair calculation.
    """
    from adaptive_question_selector import select_node_adaptive_questions, _field_node_coverage
    from short_term_repeat_guard import recent_short_term_evidence_ids
    from question_bank import question_ids, get_category_small, get_quiz_question
    from question_equivalence import canonicalize_question_evidence_id as eq

    now = _time(as_of or datetime.now(timezone.utc))
    context = daily_floor_up_context(events, now)
    if not context['active']:
        return None

    blocked = recent_short_term_evidence_ids(attempts, as_of=now) | {eq(q) for q in exclude_ids}
    recent = {
        eq(a['question_id'])
        for a in sorted(attempts, key=lambda a: _time(a['answered_at']), reverse=True)[:30]
    }
    field_map, _ = _field_node_coverage(attempts)
    learning_progress_scores = _field_learning_progress_scores(attempts)
    target_field = context['today_target_field']
    rotated = False

    if target_field:
        candidates = [row for row in strategy.get('ranked_fields') or ()
                      if int(row.get('field_id') or 0) == int(target_field)]
    else:
        candidates = _floor_up_ranked_candidates(
            strategy,
            learning_progress_scores,
            context.get('yesterday_target_field'),
        )

    required_supply = 30 if target_field else 60
    chosen = None
    for candidate in candidates:
        field_id = int(candidate['field_id'])
        eligible = {
            eq(q) for q in question_ids()
            if field_map.get(eq(q), get_category_small(q)) == field_id
        } - blocked - recent
        if len(eligible) < required_supply:
            continue
        chosen = candidate
        if (
            not target_field
            and context.get('yesterday_target_field')
            and field_id != int(context['yesterday_target_field'])
        ):
            yesterday_score = learning_progress_scores.get(
                int(context['yesterday_target_field']), {}
            ).get('learning_progress_display_percent')
            chosen_score = learning_progress_scores.get(
                field_id, {}
            ).get('learning_progress_display_percent')
            rotated = (
                yesterday_score is not None
                and chosen_score is not None
                and int(yesterday_score) == int(chosen_score)
            )
        break

    if chosen is None:
        return baseline

    field_id = int(chosen['field_id'])
    selected = select_node_adaptive_questions(
        attempts,
        30,
        exclude_ids=blocked | recent,
        category_small=field_id,
        learning_intent='repair',
        as_of=now,
        allow_spaced_repeat_fallback=True,
    )
    if len(selected) != 30:
        return baseline

    questions = [get_quiz_question(row['question_id']) for row in selected]
    if (
        len({eq(q['id']) for q in questions}) != 30
        or any(eq(q['id']) in blocked | recent for q in questions)
        or any(
            field_map.get(eq(q['id']), get_category_small(q['id'])) != field_id
            for q in questions
        )
    ):
        return baseline

    target = chosen.get('target') or {}
    evaluation = target.get('evaluation') or {}
    accuracy = evaluation.get('current_evaluable_accuracy')
    if accuracy is None:
        accuracy = evaluation.get('evaluable_accuracy')
    display_score = learning_progress_scores.get(field_id, {})
    rank_basis = {
        'learning_progress': display_score.get('learning_progress'),
        'learning_progress_display_percent': display_score.get('learning_progress_display_percent'),
        'coverage': display_score.get('coverage'),
        'accuracy': display_score.get('accuracy'),
        'finish': display_score.get('finish'),
        'answered_count': display_score.get('answered_count'),
        'strategy_accuracy': accuracy,
        'progress': target.get('current_progress_score'),
        'unresolved_repeated_weakness_nodes': target.get('unresolved_repeated_weakness_node_count', 0),
    }
    records = {row['question_id']: row for row in selected}
    updated = {}
    meta = {
        'strategy_version': VERSION,
        'strategy_recommended_field': field_id,
        'strategy_learning_intent': 'floor_up',
        'strategy_priority_score': chosen.get('priority_score', 0.0),
        'strategy_reason_codes': list(chosen.get('reason_codes') or ()) + ['daily_floor_up'],
        'strategy_priority_components': chosen.get('priority_components') or {},
        'strategy_shadow_or_authority': 'soft_pilot',
        'strategy_fallback_reason': None,
        'floor_up_mode': FLOOR_UP_VERSION,
        'floor_up_target_field': field_id,
        'floor_up_day_block': context['floor_up_day_block'],
        'floor_up_rank_basis': rank_basis,
        'floor_up_rotated_from_yesterday': rotated,
    }
    meta.update(_lifecycle_metadata(strategy))
    for q in questions:
        row = records[q['id']]
        updated[q['id']] = {
            'selection_reason': row['priority_reason'],
            'selection_group': row['priority_group'],
            'selection_score': row['priority_score'],
            'repair_evidence_quality': row['repair_evidence_quality'],
            'recent_question_repeat': False,
            'recent_cooldown_bypassed': False,
            **meta,
        }
    audit.clear()
    audit.update(updated)
    return questions


def refine_session(
    attempts, baseline, audit, events, *, exclude_ids=(), as_of=None, days_to_exam=None
):
    """Protect Safety/due and the five-slot exploration floor; soft-target the rest.

    Stage E may reroute to the next ranked field when the top field cannot fill
    the currently replaceable slots without weakening repeat/Safety guards.
    Caller must gate before loading events or importing this adapter. This
    function never reads/writes DB, changes flags, or grants the pure engine
    question-selection authority. Exceptions leave caller's baseline intact.
    """
    from adaptive_question_selector import select_node_adaptive_questions,_field_node_coverage
    from short_term_repeat_guard import recent_short_term_evidence_ids
    from question_bank import question_ids,get_category_small,get_question_tag,get_quiz_question
    from question_equivalence import canonicalize_question_evidence_id as eq
    if len(baseline)!=30:
        return baseline
    as_of=as_of or datetime.now(timezone.utc)
    strategy=strategy_snapshot(attempts, events, as_of, days_to_exam=days_to_exam)
    floor_up = _refine_floor_up_session(
        attempts, baseline, audit, strategy, events,
        exclude_ids=exclude_ids, as_of=as_of,
    )
    if floor_up is not None:
        return floor_up
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
    # Match the baseline selector's safe replay contract: only the hard real-time
    # three-day floor is an absolute repeat block here.  Older seen evidence may
    # be used as spaced fallback supply when a strategy-targeted field is saturated.
    # Formal Safety/recheck items in the baseline remain protected above.
    blocked=recent_short_term_evidence_ids(attempts,as_of=as_of)|{eq(q) for q in exclude_ids}
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
            category_small=candidate_field,learning_intent=intent,as_of=as_of,
            allow_spaced_repeat_fallback=True)
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
