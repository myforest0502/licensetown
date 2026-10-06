from copy import deepcopy

import pytest

from licensetown.pt.learning_progress_presentation import calculate_learning_progress
from licensetown.pt.overall_progress_presentation import build_overall_progress_presentation
from licensetown.pt.field_progress_presentation import (
    build_field_progress_presentation_from_calculation, format_progress_percent,
)


@pytest.mark.parametrize('coverage,accuracy,finish,expected', [
    (0, 0, 0, 0), (0.10, 0.90, 0.05, 0.081),
    (1, 0.70, 0.24, 0.652), (1, 1, 1, 1),
    (1, None, 0.24, 0.372), (-1, 2, -3, 0),
    (2, 2, 2, 1), (float('nan'), float('inf'), None, 0),
    ('invalid', {}, [], 0), (1, float('-inf'), 1, 0.6),
    (1, 0.66, 0.23, 0.633), (1, 0, 0.10, 0.33),
])
def test_learning_progress_formula_and_invalid_evidence(coverage, accuracy, finish, expected):
    assert calculate_learning_progress(coverage, accuracy, finish) == pytest.approx(expected)


def test_overall_simulation_preserves_formal_score_and_source():
    progress = {'overall': {
        'total_unique_canonical_nodes': 100,
        'touched_unique_canonical_nodes': 100,
        'state_counts': {'unseen': 0, 'repairing': 80, 'checking': 0,
                         'recheck_due': 0, 'repaired': 0, 'stable': 20},
        'overall_progress_score': 0.24,
    }}
    before = deepcopy(progress)
    row = build_overall_progress_presentation(progress, overall_accuracy_percent=70)
    assert row['learning_progress_raw'] == pytest.approx(0.652)
    assert row['learning_progress_display'] == '65%'
    assert row['progress_raw'] == 0.24
    assert row['progress_display'] == '24%'
    assert row['accuracy_display'] == '70%'
    assert row['stage_copy'].startswith('全範囲の学習は完了。')
    assert progress == before
    progress['overall']['touched_unique_canonical_nodes'] = 99
    assert 'まだ確認していない範囲' in build_overall_progress_presentation(progress)['stage_copy']


def test_field_simulation_shares_formula_and_preserves_finish():
    evidence = {'fields': [{'field_id': 1, 'question_answer_count': 100}]}
    progress = {'fields': [{'field_id': 1, 'field_name': '分野',
        'field_progress_score': 0.23, 'node_coverage': 1, 'state_counts': {}}]}
    before = deepcopy(progress)
    row, = build_field_progress_presentation_from_calculation(evidence, progress,
        legacy_fields=[{'name': '分野', 'learned': True, 'accuracy': 66, 'answered_count': 100}])
    assert row['learning_progress_raw'] == pytest.approx(0.633)
    assert row['learning_progress_display'] == '63%'
    assert row['progress_raw'] == 0.23
    assert row['progress_display'] == '23%'
    assert progress == before
    missing, = build_field_progress_presentation_from_calculation(evidence, progress)
    assert missing['accuracy_display'] == '--'
    assert missing['learning_progress_raw'] == pytest.approx(0.369)


def test_learning_progress_does_not_round_incomplete_evidence_to_100():
    progress = calculate_learning_progress(1, 0.999, 1)
    assert progress < 1
    assert format_progress_percent(progress, completed_only=True) == '99%'
    assert format_progress_percent(1, completed_only=True) == '100%'
    # Preserve the existing maturity formatter contract.
    assert format_progress_percent(progress) == '100%'
