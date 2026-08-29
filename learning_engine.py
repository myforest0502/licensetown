"""タグと保存済み履歴から学習問題を選ぶ、差し替え可能なVer1エンジン。"""

from __future__ import annotations

import random
from collections import defaultdict

from question_bank import get_question, get_question_tag, get_quiz_question, question_ids
from knowledge_node_canonical import canonicalize_knowledge_node_id


ABILITY_LABELS = {
    "KNOW": "基礎知識",
    "MEASURE": "評価や測定を選ぶ力",
    "INTERPRET": "所見から状態を読み取る力",
    "PREDICT": "経過や今後を考える力",
    "PRESCRIBE": "治療や介入を選ぶ力",
    "DECIDE": "安全性や優先順位を判断する力",
}


def _knowledge_node_key(tag):
    """Prefer the stable node ID while retaining compatibility with old tags."""
    node_id = tag.get("knowledge_node_id") or tag.get("knowledge_node")
    return canonicalize_knowledge_node_id(node_id)


def _candidate_ids(category_small=None):
    ids = list(question_ids())
    if category_small is not None:
        ids = [
            q_id for q_id in ids
            if int(get_question(q_id).get("category_small", 0)) == int(category_small)
        ]
    return ids


def build_initial_assessment(question_count=10, exclude_ids=None, rng=None):
    """能力とLevelが偏りすぎない現在地チェックを作る（最大15問）。"""
    if question_count < 1 or question_count > 15:
        raise ValueError("Initial assessment must contain 1-15 questions")
    excluded = set(exclude_ids or ())
    randomizer = rng or random
    buckets = defaultdict(list)
    for q_id in _candidate_ids():
        if q_id in excluded:
            continue
        tag = get_question_tag(q_id)
        buckets[tag.get("primary_ability")].append(q_id)
    abilities = list(buckets)
    randomizer.shuffle(abilities)
    selected = []
    used_levels = defaultdict(set)
    while abilities and len(selected) < question_count:
        next_abilities = []
        for ability in abilities:
            if not buckets[ability]:
                continue
            fresh_level = [
                q_id for q_id in buckets[ability]
                if get_question_tag(q_id).get("level") not in used_levels[ability]
            ]
            candidates = fresh_level or buckets[ability]
            chosen = randomizer.choice(candidates)
            selected.append(chosen)
            used_levels[ability].add(get_question_tag(chosen).get("level"))
            buckets[ability].remove(chosen)
            if buckets[ability]:
                next_abilities.append(ability)
            if len(selected) == question_count:
                break
        abilities = next_abilities
    if len(selected) != question_count:
        raise ValueError("Not enough tagged questions for initial assessment")
    return [get_quiz_question(q_id) for q_id in selected]


def initial_assessment_needs_extension(question_results):
    """10問時点の材料が著しく偏る場合だけ追加5問を必要とする。"""
    results = list(question_results or ())
    if len(results) < 10:
        return True
    abilities = {
        get_question_tag(result["question_id"]).get("primary_ability")
        for result in results if result.get("question_id")
    }
    levels = {
        get_question_tag(result["question_id"]).get("level")
        for result in results if result.get("question_id")
    }
    return len(abilities) < 3 or len(levels) < 2


def summarize_initial_assessment(question_results):
    """10〜15問の結果から、断定を避けた源さんの短い現在地コメントを作る。"""
    grouped = defaultdict(list)
    safety_results = []
    for result in question_results or ():
        q_id = result.get("question_id")
        if not q_id:
            continue
        tag = get_question_tag(q_id)
        grouped[tag.get("primary_ability")].append(result)
        if tag.get("safety") in {"moderate", "critical"}:
            safety_results.append(result)

    strong = []
    review = []
    guessed_count = 0
    confident_error_count = 0
    for ability, results in grouped.items():
        guessed_count += sum(int(result.get("confidence") == 3) for result in results)
        confident_error_count += sum(
            int(not result.get("is_correct") and result.get("confidence") == 1)
            for result in results
        )
        if len(results) < 2:
            continue
        strong_count = sum(
            int(result.get("is_correct") and result.get("confidence") == 1)
            for result in results
        )
        check_count = sum(
            int(not result.get("is_correct") or result.get("confidence") == 3)
            for result in results
        )
        if strong_count / len(results) >= 0.67:
            strong.append((strong_count / len(results), ABILITY_LABELS[ability]))
        elif check_count / len(results) >= 0.5:
            review.append((check_count / len(results), ABILITY_LABELS[ability]))

    strong_labels = [label for _score, label in sorted(strong, reverse=True)[:2]]
    review_labels = [label for _score, label in sorted(review, reverse=True)[:2]]
    lines = ["おう！お前の現在地はだいたい分かったぞ。", ""]

    if strong_labels:
        lines.append(f"今のところ、{strong_labels[0]}はかなり安定してそうだ。")
        if len(strong_labels) > 1:
            lines.append(f"{strong_labels[1]}もいい感じだ。")
    else:
        lines.append("今はまだ、知識や考え方を確認したい所がいくつかある。")

    if review_labels:
        lines.append(f"ただ、{review_labels[0]}はもう少し別の問題でも確認したいな。")
        if len(review_labels) > 1:
            lines.append(f"{review_labels[1]}も、まだ様子を見ていこう。")
        if guessed_count >= 2:
            lines.append("自信度を見ると、迷いながら答えた所も少しある。")
        elif confident_error_count:
            lines.append("自信を持って選んだ所も、考え方をもう一度確かめよう。")
    elif guessed_count >= 2:
        lines.append("正解できていても、迷いながら答えた所はもう一度確認していこう。")
    elif confident_error_count:
        lines.append("自信を持って選んだ所も、別の問題で考え方を確かめていこう。")
    else:
        lines.append("まだ問題数は少ないから、別の問題でも安定してるか見ていくぞ。")

    if len(safety_results) >= 2 and all(result.get("is_correct") for result in safety_results):
        lines.append("安全に関わる判断もしっかりできてる。")

    if not strong_labels:
        lines.append("いきなり難しい問題ばかりにはせず、解ける所から土台を作ろう。")
    else:
        lines.append("できてる所を無駄に繰り返さず、確認したい所と新しい問題を混ぜていくぞ。")
    lines.extend([
        "", "心配するなｗ", "これはあくまでも現在位置だ。", "ここからが勝負だぜ＾＾",
    ])
    return "\n".join(lines)


def build_daily_session(
    history, question_count=30, category_small=None, exclude_ids=None, rng=None
):
    """誤概念候補・未習得候補・新規領域を優先した30問を返す。"""
    randomizer = rng or random
    latest = {}
    node_results = defaultdict(list)
    for result in history or ():
        q_id = str(result.get("question_id", "")).upper()
        if not q_id:
            continue
        latest[q_id] = result
        node = _knowledge_node_key(get_question_tag(q_id))
        node_results[node].append(bool(result.get("is_correct")))

    excluded = set(exclude_ids or ())
    scored = []
    for q_id in _candidate_ids(category_small):
        if q_id in excluded:
            continue
        tag = get_question_tag(q_id)
        result = latest.get(q_id)
        if result is None:
            score = 250
        elif not result.get("is_correct") and result.get("confidence") == 1:
            score = 600
        elif not result.get("is_correct"):
            score = 500
        elif result.get("confidence") == 3:
            score = 400
        else:
            score = 50
        node_history = node_results.get(_knowledge_node_key(tag), ())
        if len(node_history) >= 2 and sum(node_history) / len(node_history) < 0.6:
            score += 150
        if tag.get("safety") not in {None, "", "none"}:
            score += 20
        scored.append((score, randomizer.random(), q_id))
    scored.sort(reverse=True)
    selected = [q_id for _score, _tie, q_id in scored[:question_count]]
    if len(selected) < question_count:
        raise ValueError("Not enough questions for daily session")
    return [get_quiz_question(q_id) for q_id in selected]


def summarize_daily_session(question_results):
    """30問の正誤と自信度を、非断定的な短い結果表示へまとめる。"""
    results = list(question_results or ())
    grouped = defaultdict(list)
    for result in results:
        q_id = result.get("question_id")
        if q_id:
            grouped[get_question_tag(q_id).get("primary_ability")].append(result)

    stable = []
    checking = []
    revisit = []
    for ability, ability_results in grouped.items():
        if len(ability_results) < 2:
            continue
        confident_correct = sum(
            int(result.get("is_correct") and result.get("confidence") == 1)
            for result in ability_results
        )
        high_priority = sum(
            int(not result.get("is_correct") and result.get("confidence") == 1)
            for result in ability_results
        )
        uncertain = sum(
            int(not result.get("is_correct") or result.get("confidence") in {2, 3})
            for result in ability_results
        )
        label = ABILITY_LABELS[ability]
        if confident_correct / len(ability_results) >= 0.67:
            stable.append((confident_correct, label))
        if high_priority >= 2:
            revisit.append((high_priority, label))
        elif uncertain / len(ability_results) >= 0.5:
            checking.append((uncertain, label))

    score = sum(int(result.get("is_correct")) for result in results)
    lines = ["おう、今日の30問お疲れさん＾＾", "", f"今日の結果　{score} / {len(results)}"]
    if stable:
        lines.extend(["", "今日できていたところ", f"・{sorted(stable, reverse=True)[0][1]}"])
    if checking:
        lines.extend(["", "確認中", f"・{sorted(checking, reverse=True)[0][1]}"])
    if revisit:
        lines.extend(["", "次回もう一度", f"・{sorted(revisit, reverse=True)[0][1]}"])
    if not (stable or checking or revisit):
        lines.extend(["", "まだ判断材料が少ない所は、次回も別の問題で見ていくぞ。"])
    lines.extend([
        "", "1回の間違いだけで決めつけないから安心しろｗ",
        "まだ確認したい所は、次回こっちで混ぜておくぞ。",
    ])
    return "\n".join(lines)


def select_questions_for_session(
    kind, history=None, question_count=30, category_small=None, exclude_ids=None
):
    """UIから利用する共通入口。"""
    if kind == "initial_assessment":
        return build_initial_assessment(question_count)
    return build_daily_session(
        history or (), question_count, category_small, exclude_ids=exclude_ids
    )
