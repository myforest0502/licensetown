"""Offline Stage F replay. No DB, network, runtime callers or authority.

Input is a SELECT-only export for one anonymous PT learner. Keep that export
outside Git. Only aggregate checkpoint outputs are suitable for publication.
"""
from __future__ import annotations

import argparse
import builtins
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
INTENTS = ('coverage', 'repair', 'retention', 'attainment', 'maintenance',
           'safety_review', 'strategy_change', 'defer')
MISSING_BLOCK_CONTEXT = ['additional_blocks_completed', 'consecutive_field_blocks']


def _deny_database(*args, **kwargs):
    raise RuntimeError('Database access is forbidden in offline audit')


def _evidence_builder():
    # The existing evidence module imports a DB adapter whose module initializes
    # the DB. Supply an inert adapter only in this private module's builtins.
    # Do not replace sys.modules, environment, or any Production module/function.
    original_import = builtins.__import__

    def offline_import(name, *args, **kwargs):
        if name == 'database':
            return SimpleNamespace(get_question_attempts=_deny_database)
        return original_import(name, *args, **kwargs)

    spec = importlib.util.spec_from_file_location('_offline_field_evidence', ROOT / 'field_evidence.py')
    module = importlib.util.module_from_spec(spec)
    module.__dict__['__builtins__'] = dict(vars(builtins), __import__=offline_import)
    spec.loader.exec_module(module)
    return module.build_field_evidence


def _time(value):
    result = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('UTC offset required')
    return result.astimezone(timezone.utc)


def normalize(records):
    """Whitelist fields; discard all original identities and arbitrary metadata."""
    rows = []
    for source in records:
        rows.append({
            'user_id': 'anonymous-audit',
            'id': int(source['id']),
            'event_key': f"event-{int(source['event_number']):012d}",
            'question_id': source['question_id'],
            'knowledge_node_id': source['knowledge_node_id'],
            'is_correct': source['is_correct'] is True,
            'confidence': source.get('confidence'),
            'answered_at': _time(source['answered_at']),
            'attempt_position': int(source['attempt_position']),
            'selected_answers': list(source.get('selected_answers') or []),
            # Match dashboard_read_bundle / database.get_question_attempts.
            'answer_status': 'answered' if source.get('selected_answers') else 'unknown',
            'selection_group': source.get('selection_group') if source.get('selection_group') in
                {'repair', 'checking', 'exploration', 'maintenance'} else None,
        })
    rows.sort(key=lambda a: (a['answered_at'], a['event_key'], a['attempt_position'], a['id']))
    if not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Nonempty unique attempts required')
    return rows


def checkpoint_positions(rows, step=30):
    """Move cuts to the end of timestamp ties: never split an atomic event."""
    positions = set()
    for n in range(step, len(rows), step):
        while n < len(rows) and rows[n]['answered_at'] == rows[n-1]['answered_at']:
            n += 1
        positions.add(n)
    return sorted(positions | {len(rows)})


def eligible_supply(attempts, field_id, as_of):
    from adaptive_question_selector import _attempt_time, _field_node_coverage
    from question_bank import question_ids, get_category_small
    from question_equivalence import canonicalize_question_evidence_id as eq
    from short_term_repeat_guard import blocked_short_term_evidence_ids
    blocked = blocked_short_term_evidence_ids(attempts, as_of=as_of)
    recent = {eq(a['question_id']) for a in sorted(attempts, key=_attempt_time, reverse=True)[:30]}
    fields, _ = _field_node_coverage(attempts)
    raw_recent = {a['question_id'] for a in attempts if as_of-a['answered_at'] < timedelta(days=3)}
    bank = [q for q in question_ids() if fields.get(eq(q), get_category_small(q)) == field_id]
    after_raw = [q for q in bank if q not in raw_recent]
    after_formal = {eq(q) for q in after_raw if eq(q) not in blocked}
    eligible = after_formal - recent
    return {'static_raw_supply': len(bank), 'after_raw_72h': len(after_raw),
            'after_exact_and_formal_state': len(after_formal), 'eligible_supply': len(eligible),
            'eligible_supply_insufficient': len(eligible) < 30,
            'cooldown_relaxed': False}


def safety_context(attempts, as_of):
    from adaptive_question_selector import _node_attempt_summary, _priority
    from knowledge_node_state_transition import derive_all_user_node_states
    from question_bank import question_ids, get_question_tag, get_category_small
    from question_equivalence import canonicalize_question_evidence_node as node
    states = {r['canonical_node_id']: r['state'] for r in derive_all_user_node_states(attempts, as_of=as_of)}
    summaries = _node_attempt_summary(attempts)
    unresolved = defaultdict(set)
    for q in question_ids():
        tag = get_question_tag(q)
        n = node(q, tag['knowledge_node_id'])
        if tag.get('safety') == 'critical' and n in summaries:
            _, reason, _ = _priority(states.get(n, 'unseen'), summaries[n], 'critical')
            if reason in {'safety_wrong', 'safety_unresolved'}:
                unresolved[get_category_small(q)].add(n)
    return {f: len(unresolved[f]) for f in range(1, 19)}


def replay(records):
    from field_progress import build_field_progress
    from learning_strategy_shadow import build_learning_strategy
    from question_bank import get_category_small, question_ids
    from question_equivalence import canonicalize_question_evidence_id as eq
    rows = normalize(records)
    bank = set(question_ids())
    if any(a['question_id'] not in bank for a in rows):
        raise ValueError('Unknown bank question')
    build_evidence = _evidence_builder()
    repeat_counts = Counter()
    last_raw, last_exact = {}, {}
    guard_merged_at = _time('2026-09-12T04:35:45+00:00')
    for a in rows:
        q, at = a['question_id'], a['answered_at']
        identity = eq(q)
        post = at >= guard_merged_at
        repeat_counts['post_337_attempts'] += int(post)
        if q in last_raw and at-last_raw[q] < timedelta(days=3):
            repeat_counts['all_history_same_q_72h'] += 1
            repeat_counts['post_337_same_q_72h'] += int(post)
        if identity in last_exact and at-last_exact[identity][0] < timedelta(days=3):
            repeat_counts['all_history_exact_72h'] += 1
            repeat_counts['post_337_exact_72h'] += int(post)
            repeat_counts['post_337_cross_q_exact_72h'] += int(post and last_exact[identity][1] != q)
        last_raw[q], last_exact[identity] = at, (at,q)
    checkpoints, previous = [], {}
    streak_field, streak = None, 0
    for n in checkpoint_positions(rows):
        prefix, as_of = rows[:n], rows[n-1]['answered_at']
        evidence = build_evidence(prefix, as_of=as_of)
        progress = build_field_progress(evidence)
        critical = safety_context(prefix, as_of)
        last_study = {get_category_small(a['question_id']): a['answered_at'] for a in prefix}
        contexts = {}
        for p in progress['fields']:
            f = p['field_id']
            c = {'critical_safety_unresolved_count': critical[f]}
            if f in last_study:
                c['days_since_last_field_study'] = (as_of-last_study[f]).total_seconds()/86400
            if f in previous:
                c.update(previous[f])
            contexts[f] = c
        # Learner-specific exam date is not in the export; do not invent it.
        strategy = build_learning_strategy(evidence, progress, context_by_field=contexts)
        ranked = strategy['ranked_fields']
        f = strategy['recommended_field_id']
        streak = streak+1 if f is not None and f == streak_field else int(f is not None)
        streak_field = f
        next_rows = rows[n:n+30]
        actual = Counter(get_category_small(a['question_id']) for a in next_rows)
        # Resolve ties deterministically by field ID, expose the tied modes too.
        modal = sorted(actual, key=lambda k: (-actual[k], k))
        selected = next((r for r in ranked if r['field_id'] == f), None)
        cp = {'answers': n, 'as_of': as_of.isoformat(), 'recommended_field_id': f,
              'learning_intent': strategy['learning_intent'], 'recommendation_streak': streak,
              'next_answer_count': len(next_rows), 'actual_next_fields': dict(actual),
              'actual_modal_fields': [k for k in modal if actual[k] == actual[modal[0]]] if modal else [],
              'top1_match': f == modal[0] if len(next_rows) == 30 else None,
              'top3_match': modal[0] in [r['field_id'] for r in ranked[:3]] if len(next_rows) == 30 else None,
              'actual_next_selection_groups': dict(Counter(a['selection_group'] or 'unavailable' for a in next_rows)),
              'critical_safety_nodes': sum(critical.values()),
              'safety_priority_contradiction': bool(any(critical.values()) and strategy['learning_intent'] != 'safety_review'),
              'selected_components': selected['priority_components'] if selected else {},
              'selected_exam_weight': selected['target']['exam_weight']['relative_weight'] if selected else None,
              'selected_field_state': selected['field_state'] if selected else None,
              'missing_context': MISSING_BLOCK_CONTEXT + ['days_to_exam'],
              'shadow_only': True, 'selection_authority': False}
        if f is not None:
            cp.update(eligible_supply(prefix, f, as_of))
        checkpoints.append(cp)
        previous = {p['field_id']: {'previous_progress_score': p['field_progress_score'],
                    'previous_stable_ratio': p['state_counts']['stable']/max(1,p['touched_canonical_nodes'])}
                    for p in progress['fields']}
    final = []
    by_field = {e['field_id']: e for e in evidence['fields']}
    milestone_counts, milestone_dates = Counter(), defaultdict(dict)
    for a in rows:
        if a['answer_status'] != 'unknown':
            f = get_category_small(a['question_id'])
            milestone_counts[f] += 1
            if milestone_counts[f] in (60,90,120,150):
                milestone_dates[f][milestone_counts[f]] = a['answered_at'].isoformat()
    for rank, r in enumerate(ranked, 1):
        t, e = r['target'], by_field[r['field_id']]
        evaluation = t['evaluation']
        limitations = []
        if e['evaluable_answer_count'] < 60:
            limitations.append('question_floor_insufficient')
        if evaluation['touched_canonical_nodes'] < evaluation['required_node_spread']:
            limitations.append('node_spread_insufficient')
        if e['total_question_count'] < 60:
            limitations.append('small_supply_limitation')
        final.append({'field_id': r['field_id'], 'field_name': r['field_name'],
            'evaluable_answer_count': e['evaluable_answer_count'], 'accuracy': e['evaluable_accuracy'],
            'total_questions': e['total_question_count'], 'total_nodes': t['total_canonical_nodes'],
            'touched_nodes': evaluation['touched_canonical_nodes'],
            'required_node_spread': evaluation['required_node_spread'],
            'coverage': e['node_coverage']['percent']/100, 'progress_score': t['current_progress_score'],
            'field_state': 'assessing' if 'small_supply_limitation' in limitations else r['field_state'],
            'raw_shadow_field_state': r['field_state'], 'recovery_level': r['recovery_level'],
            'exam_weight': t['exam_weight']['relative_weight'],
            'target_progress': t['target_progress_score'], 'target_stable': t['target_stable_ratio'],
            'target_resolved': t['target_resolved_ratio'], 'maintenance_needed': t['maintenance_needed'],
            'priority_score': r['priority_score'], 'learning_intent': r['learning_intent'], 'rank': rank,
            'reason_codes': r['reason_codes'], 'evaluation_status': limitations or ['evaluation_sufficient'],
            'critical_safety_unresolved_count': t['critical_safety_unresolved_count'],
            'historical_proxy_only_milestones': milestone_dates[r['field_id']]})
    compared = [c for c in checkpoints if c['next_answer_count'] == 30]
    supplied = [c for c in checkpoints if c['recommended_field_id'] is not None]
    reasons = ['additional_and_consecutive_block_context_unavailable',
               'observational_replay_cannot_establish_coverage_noninferiority',
               'single_learner_no_prospective_shadow_following_outcomes']
    if any(c['eligible_supply_insufficient'] for c in supplied):
        reasons.append('eligible_supply_insufficient')
    if any(c['recommendation_streak'] > 3 for c in checkpoints):
        reasons.append('repeated_recommendations_exceed_three_observations')
    if any('small_supply_limitation' in f['evaluation_status'] and f['raw_shadow_field_state'] in {'weak','strong'} for f in final):
        reasons.append('small_supply_classification_policy_conflict')
    # No arbitrary acceptance percentage fitted to the observed results.
    return {'version': 'stage_f_v1', 'shadow_only': True, 'selection_authority': False,
        'observed_repeat_counts': {k: repeat_counts[k] for k in (
            'post_337_attempts', 'all_history_same_q_72h', 'all_history_exact_72h',
            'post_337_same_q_72h','post_337_exact_72h','post_337_cross_q_exact_72h')},
        'judgment': 'HOLD', 'production_connection': 'NOT YET', 'hold_reasons': reasons,
        'history': {'attempts': len(rows), 'distinct_questions': len({a['question_id'] for a in rows}),
                    'distinct_raw_nodes': len({a['knowledge_node_id'] for a in rows}),
                    'accuracy': sum(a['is_correct'] for a in rows)/len(rows),
                    'unknown_answers': sum(a['answer_status'] == 'unknown' for a in rows),
                    'first': rows[0]['answered_at'].isoformat(), 'last': rows[-1]['answered_at'].isoformat()},
        'summary': {'checkpoint_count': len(checkpoints), 'comparison_count': len(compared),
                    'top1_matches': sum(c['top1_match'] for c in compared),
                    'top3_matches': sum(c['top3_match'] for c in compared),
                    'recommended_fields': dict(Counter(c['recommended_field_id'] for c in checkpoints)),
                    'intent_counts': {i: sum(c['learning_intent']==i for c in checkpoints) for i in INTENTS},
                    'supply_sufficient': sum(not c['eligible_supply_insufficient'] for c in supplied),
                    'supply_checked': len(supplied), 'max_recommendation_streak': max(c['recommendation_streak'] for c in checkpoints),
                    'safety_priority_contradictions': sum(c['safety_priority_contradiction'] for c in checkpoints),
                    'high_weight_recommendations': sum(c['selected_exam_weight'] >= 1 for c in supplied),
                    'low_weight_weak_recommendations': sum(c['selected_exam_weight'] < 1 and c['selected_field_state']=='weak' for c in supplied)},
        'checkpoints': checkpoints, 'final_fields': sorted(final,key=lambda f:f['field_id'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('anonymous_input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = replay(json.loads(args.anonymous_input.read_text(encoding='utf-8')))
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result['summary'],ensure_ascii=False))


if __name__ == '__main__':
    main()
