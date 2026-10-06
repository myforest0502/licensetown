import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render(*, finish=23.8, coverage=100, accuracy=69, days=137, learning_progress=None):
    if learning_progress is None:
        learning_progress = 0.30 * (coverage / 100) + 0.40 * (coverage / 100) * (accuracy / 100) + 0.30 * (finish / 100)
    snapshot = {
        'daysUntilExam': days,
        'totalAnswers': 6236,
        'uniqueAnsweredQuestions': 2741,
        'overall': {
            'progress_raw': finish / 100,
            'coverage_raw': coverage / 100,
            'learning_progress_raw': learning_progress,
        },
        'accuracy': accuracy,
        'fields': [],
        'navigation': None,
    }
    result = subprocess.run(
        ['node', 'tests/recommended_route_guidance_runner.js'],
        cwd=ROOT, input=json.dumps(snapshot), text=True, capture_output=True, check=True,
    )
    return json.loads(result.stdout)['html']


def test_restores_compact_three_card_route_layout():
    html = render()
    assert 'lt-route-pace-panel' in html
    assert '<div class="lt-route-now-grid">' in html
    assert '<div class="lt-route-timeline"' in html
    assert 'lt-route-hero' not in html
    assert '今の状態・不足しているポイント' not in html


def test_137_day_case_uses_balanced_learning_progress_not_raw_finish_percentages():
    html = render()
    assert '残り137日' in html
    assert '約5日先行' in html
    assert '<small>この時点の推奨</small><strong>64%</strong><span>LT学習進捗</span>' in html
    assert '<small>現在</small><strong>65%</strong><span>推奨との差 +0.7pt</span>' in html
    assert '21.5%' not in html
    assert '23.8%' not in html


def test_balanced_score_is_grounded_in_scope_accuracy_and_strict_finish():
    html = render(finish=24, coverage=100, accuracy=70, days=137)
    # Current = 30 + 28 + 7.2 = 65.2 -> 65%
    # Recommended strict finish at 137d = 21.5%, so displayed recommendation:
    # 30 + 28 + 6.45 = 64.45 -> 64%
    assert '<small>この時点の推奨</small><strong>64%</strong>' in html
    assert '<small>現在</small><strong>65%</strong>' in html
    assert '学習範囲・正答率・知識の仕上がりを合わせた今日の目安' in html


def test_behind_case_remains_truthful_and_shows_days_behind():
    html = render(finish=17.5)
    assert '約8日遅れ' in html
    assert '少し巻き返したい' in html
    assert '21.5%' not in html
    assert '17.5%' not in html


def test_route_disclaimer_explains_display_and_strict_pace_authority():
    html = render()
    assert '数字は学習範囲・正答率・知識の仕上がりを合わせたLT学習進捗です' in html
    assert '合格確率ではありません' in html
    assert '先行／遅れの判定は厳密な知識の仕上がりを試験日から逆算して行います' in html
