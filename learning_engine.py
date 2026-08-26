"""タグと保存済み履歴から学習問題を選ぶ、差し替え可能なVer1エンジン。"""

from __future__ import annotations

import random
from collections import defaultdict

from question_bank import get_question, get_question_tag, get_quiz_question, question_ids


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


def build_daily_session(history, question_count=30, category_small=None, rng=None):
    """誤概念候補・未習得候補・新規領域を優先した30問を返す。"""
    randomizer = rng or random
    latest = {}
    node_results = defaultdict(list)
    for result in history or ():
        q_id = str(result.get("question_id", "")).upper()
        if not q_id:
            continue
        latest[q_id] = result
        node = get_question_tag(q_id).get("knowledge_node")
        node_results[node].append(bool(result.get("is_correct")))

    scored = []
    for q_id in _candidate_ids(category_small):
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
        node_history = node_results.get(tag.get("knowledge_node"), ())
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


def select_questions_for_session(kind, history=None, question_count=30, category_small=None):
    """UIから利用する共通入口。"""
    if kind == "initial_assessment":
        return build_initial_assessment(question_count)
    return build_daily_session(history or (), question_count, category_small)
