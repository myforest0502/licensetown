from datetime import datetime, timezone

import adaptive_question_selector as selector
import learning_strategy_runtime_pilot as pilot
from question_bank import get_category_small, get_question_tag, get_quiz_question, question_ids
from question_equivalence import canonicalize_question_evidence_id as eq


NOW = datetime(2026, 9, 17, tzinfo=timezone.utc)


def _field_pool(field_id):
    fields, _ = selector._field_node_coverage([])
    pool = []
    seen = set()
    for qid in question_ids():
        evidence_id = eq(qid)
        if fields[evidence_id] == field_id and evidence_id not in seen:
            pool.append(qid)
            seen.add(evidence_id)
    return pool


def _safe_outside(*field_ids):
    fields, _ = selector._field_node_coverage([])
    return [
        qid for qid in question_ids()
        if fields[eq(qid)] not in set(field_ids)
        and get_question_tag(qid).get('safety') not in {'critical', 'high', 'moderate'}
    ]


def _row(field_id, score, intent='coverage'):
    return {
        'field_id': field_id,
        'learning_intent': intent,
        'priority_score': score,
        'reason_codes': ['coverage_insufficient'],
        'priority_components': {'coverage_gap_score': 1.0},
        'allocation_candidate': True,
    }


def _strategy(*rows):
    first = rows[0]
    return {
        'recommended_field_id': first['field_id'],
        'learning_intent': first['learning_intent'],
        'priority_score': first['priority_score'],
        'reason_codes': first['reason_codes'],
        'priority_components': first['priority_components'],
        'ranked_fields': list(rows),
    }


def test_ranked_strategy_protects_only_five_exploration_floor_slots(monkeypatch):
    pool = _field_pool(2)
    assert len(pool) >= 25
    baseline = [get_quiz_question(qid) for qid in _safe_outside(2)[:30]]
    audit = {
        q['id']: {
            'selection_group': 'exploration',
            'selection_reason': 'unseen',
            'recent_question_repeat': False,
            'recent_cooldown_bypassed': False,
        }
        for q in baseline
    }
    monkeypatch.setattr(pilot, 'strategy_snapshot', lambda *a, **k: _strategy(_row(2, 1.4)))
    excluded = {eq(qid) for qid in pool[25:]}

    result = pilot.refine_session([], baseline, audit, [], exclude_ids=excluded, as_of=NOW)
    ids = {q['id'] for q in result}

    assert len(result) == len(ids) == 30
    assert {q['id'] for q in baseline[:pilot.EXPLORATION_FLOOR]} <= ids
    assert sum(get_category_small(q['id']) == 2 for q in result) == 25
    assert all(row['strategy_shadow_or_authority'] == 'soft_pilot' for row in audit.values())


def test_ranked_strategy_reroutes_when_top_field_lacks_current_supply(monkeypatch):
    field2 = _field_pool(2)
    field3 = _field_pool(3)
    assert len(field2) >= 1 and len(field3) >= 6
    baseline = [get_quiz_question(qid) for qid in _safe_outside(2, 3)[:30]]
    audit = {}
    for i, q in enumerate(baseline):
        if i < 5:
            group, reason = 'exploration', 'unseen'
        elif i < 24:
            group, reason = 'checking', 'recheck_due'
        else:
            group, reason = 'checking', 'uncertain_correct'
        audit[q['id']] = {
            'selection_group': group,
            'selection_reason': reason,
            'recent_question_repeat': False,
            'recent_cooldown_bypassed': False,
        }
    monkeypatch.setattr(
        pilot,
        'strategy_snapshot',
        lambda *a, **k: _strategy(_row(2, 1.5, 'safety_review'), _row(3, 1.2, 'coverage')),
    )
    excluded = {eq(qid) for qid in field2[1:]} | {eq(qid) for qid in field3[6:]}

    result = pilot.refine_session([], baseline, audit, [], exclude_ids=excluded, as_of=NOW)

    assert len(result) == 30
    assert sum(get_category_small(q['id']) == 3 for q in result) == 6
    assert all(row['strategy_recommended_field'] == 3 for row in audit.values())
    assert all('eligible_supply_reroute' in row['strategy_reason_codes'] for row in audit.values())
    assert all(row['strategy_shadow_or_authority'] == 'soft_pilot' for row in audit.values())
