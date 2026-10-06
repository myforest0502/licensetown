import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def render(*, finish=23.8, coverage=100, accuracy=69, days=137, **extra):
    snapshot = {
        'daysUntilExam': days,
        'overall': {'progress_raw': finish / 100, 'coverage_raw': coverage / 100},
        'accuracy': accuracy,
        'fields': [{'name': '優先分野', 'progress_raw': .17}],
        'navigation': {
            'attention_items': [{'field': '優先分野', 'label': '再確認の時期', 'message': '既存の再確認理由'}],
            'today_action': {'field': '優先分野', 'count': 10, 'learning_intent': 'recheck', 'reason': '既存の再確認理由'},
        },
        **extra,
    }
    result = subprocess.run(['node', 'tests/recommended_route_guidance_runner.js'], cwd=ROOT,
                            input=json.dumps(snapshot), text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def test_a_ahead_uses_existing_inverse_finish_curve_and_primary_time_display():
    result = render()
    assert result['model']['recommended'] == 21.5
    assert result['model']['deltaDays'] == 5
    hero = result['html'].split('class="lt-route-hero"')[1].split('</div>')[0]
    assert '試験まであと137日' in hero
    assert '約5日先行' in hero
    assert '%' not in hero
    assert '約5日先行' in result['glance']
    assert '今日の目安は満たしています' in result['html']


def test_b_late_explains_actual_shortage_and_preserves_strategy_priority():
    result = render(finish=17.5)
    assert result['model']['deltaDays'] == -8
    assert '約8日遅れています' in result['html']
    assert 'あと4pt' in result['html']
    assert '今いちばん足りないもの：知識の仕上がり' in result['html']
    assert '特に優先する分野' in result['html']
    assert '仕上がり 17%' not in result['html']
    assert '優先分野を10問' in result['html']
    assert '＋再確認問題を優先' in result['html']
    assert result['clicked']  # forwards to the same authorized existing CTA


def test_c_complete_scope_is_sufficient_and_f_ahead_does_not_fabricate_shortages():
    result = render()
    assert '十分・不足なし' in result['html']
    assert result['model']['shortages'] == []
    assert 'あと' not in result['html'].split('data-route-metric="coverage"')[1].split('</div>')[0]
    assert 'has-shortage' not in result['html']
    assert '今いちばん足りないもの' not in result['html']


def test_d_accuracy_gap_only_uses_explicit_source_criterion():
    result = render(recommendedAccuracy=75)
    assert '推奨 75% / 現在 69%' in result['html']
    assert 'あと6pt' in result['html']
    assert result['model']['shortages'][0]['key'] == 'accuracy'
    without_criterion = render()
    assert '推奨 75%' not in without_criterion['html']
    accuracy_row = without_criterion['model']['metrics'][1]
    assert accuracy_row['recommended'] is None and accuracy_row['shortage'] is None
    assert '今日の推奨基準は未設定' in without_criterion['html']


def test_e_finish_shortage_uses_current_day_curve():
    result = render(days=108, finish=24)
    assert result['model']['recommended'] == 38
    assert '推奨 38% / 現在 24%' not in result['html']
    assert '今日の目安まであと14pt' in result['html']


def test_g_raw_finish_percentages_are_hidden_and_disclaimer_is_visible():
    result = render()
    details = result['html'].split('<details class="lt-route-supplement">')[1]
    assert 'この時点の推奨：21.5% / 現在：23.8%' not in result['html']
    assert '21.5%' not in result['html']
    assert '23.8%' not in result['html']
    assert '厳密な仕上がり率の絶対値は、この推奨ルートでは表示しません' in details
    assert '<details open' not in result['html']
    assert '合格確率ではありません' in result['html'].split('<details')[0]
    for forbidden in ['もう安心', '合格確実', '合格圏', 'しか進んでいません']:
        assert forbidden not in result['html']


@pytest.mark.parametrize('days', [None, '', 'invalid'])
def test_unknown_or_expired_date_never_becomes_exam_day(days):
    result = render(days=days)
    assert result['model']['deltaDays'] is None
    assert '試験日は未設定' in result['html']
    assert '今日は試験日' not in result['html']


def test_exam_day_and_missing_evidence_are_distinguished():
    assert '今日は試験日' in render(days=0)['html']
    result = render(overall=None, accuracy=None, navigation=None)
    assert result['model']['finish'] is None
    assert result['model']['deltaDays'] is None
    assert '位置を確認中' in result['html']
    assert '記録なし' in result['html']
    assert 'NaN' not in result['html']


def test_priority_order_maximum_three_and_html_escaping():
    items = [{'field': name, 'label': '修復中', 'message': '<img src=x onerror=bad>'}
             for name in ['最優先', '次の分野', '三番目', '四番目']]
    result = render(finish=17.5, navigation={'attention_items': items, 'today_action': {}})
    assert result['html'].index('最優先') < result['html'].index('次の分野') < result['html'].index('三番目')
    assert '四番目' not in result['html']
    assert '<img src=x' not in result['html']
    assert '&lt;img' in result['html']


def test_preview_has_no_active_route_action():
    result = render(preview=True)
    assert result['buttonRemoved'] and not result['clicked']


def test_snapshot_preserves_null_date_and_serializes_existing_sources():
    base = (ROOT / 'templates/goukaku/base.html').read_text()
    assert 'dashboard.days_until_exam|default(none)|tojson' in base
    assert 'dashboard.overall_progress_preview|default(none)|tojson' in base
    assert 'dashboard.learner_navigation|default(none)|tojson' in base


def test_past_exam_and_small_lag_are_not_mislabeled():
    assert '試験日を過ぎています' in render(days=-1)['html']
    result = render(days=300, finish=.99)
    assert result['model']['deltaDays'] < 0
    assert result['model']['shortages']
    assert '不足は0.1pt未満' in result['html']
