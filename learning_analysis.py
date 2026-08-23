"""学習履歴から苦手分野と今日のおすすめを決定論的に選ぶ。"""

from __future__ import annotations

from typing import Any

from question_bank import BASIC_CATEGORY_SMALLS


FOUNDATION_ANSWER_THRESHOLD = 100
MIN_RELIABLE_ANSWERS = 10

GENSAN_FEEDBACK_TEMPLATES = (
    "{praise}はよう頑張ってんなぁ＾＾\n今日は{next}を5問だけいってみるか？",
    "{praise}、いい感じだぞ＾＾\n次は{next}を少しやってみようか。",
    "{praise}はだいぶ積み上がってきたなぁ。\n今日は{next}をちょっと触ってみるか＾＾",
    "{praise}はちゃんと続いてるな＾＾\n{next}も10問くらいやればもっと見えてくるぞ。",
    "{praise}は強くなってきたなぁ＾＾\n次は{next}を少しずつ埋めていこう。",
)


def build_recommendation_reason(
    field_name: str,
    question_count: int,
    reason: str | None,
) -> str:
    """既存の苦手判定理由を、おすすめ学習用の短い説明に変換する。"""
    if reason == "取り組み不足":
        return (
            "まだ回答数が少なく、実力判定のデータが足りません。"
            f"まず{question_count}問取り組んで傾向を確認してみよう。"
        )
    if reason == "正答率が低い":
        return (
            f"{field_name}は現在の正答率が低く、優先して復習したい分野です。"
            f"{question_count}問取り組んで苦手なポイントを確認してみよう。"
        )
    if reason == "他分野より正答率が低い":
        return (
            f"{field_name}は他の分野と比べて正答率が低くなっています。"
            f"今のうちに{question_count}問取り組んで理解を固めておこう。"
        )
    if reason == "未学習":
        return (
            f"{field_name}はまだ取り組んでいない分野です。"
            f"まず{question_count}問解いて、現在の理解度を確認してみよう。"
        )
    return (
        f"{field_name}は今の学習状況から、次に取り組む優先度が高い分野です。"
        f"{question_count}問解いて理解をさらに深めてみよう。"
    )


def _foundation_recommendation(fields: list[dict[str, Any]]) -> dict[str, Any] | None:
    basics = [item for item in fields if item["category_small"] in BASIC_CATEGORY_SMALLS]
    if not basics:
        return None

    def priority(item):
        answered = item["answered_count"]
        # 未学習→回答数が少ない→信頼度を補正した正答率の順。
        smoothed_accuracy = (
            (item["correct_count"] + 3) / (answered + 5) * 100
            if answered else 50
        )
        return (answered > 0, answered, smoothed_accuracy, item["category_small"])

    return min(basics, key=priority)


def _weakness_candidates(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    detailed_answers = sum(item["answered_count"] for item in fields)
    learned_fields = [item for item in fields if item["answered_count"] > 0]
    reliable_fields = [
        item for item in fields if item["answered_count"] >= MIN_RELIABLE_ANSWERS
    ]
    reliable_answers = sum(item["answered_count"] for item in reliable_fields)
    user_accuracy = (
        sum(item["correct_count"] for item in reliable_fields) / reliable_answers * 100
        if reliable_answers else None
    )
    expected_answers = detailed_answers / len(fields) if fields else 0
    broad_enough = detailed_answers >= 60 and len(learned_fields) >= 6
    candidates = []

    for item in fields:
        answered = item["answered_count"]
        accuracy = item["accuracy"]
        if answered == 0 or answered < MIN_RELIABLE_ANSWERS:
            continue
        confidence = min(answered / 15, 1.0)
        absolute_deficit = max(70 - accuracy, 0)
        relative_deficit = max((user_accuracy or accuracy) - accuracy, 0)
        shortage = (
            max(expected_answers - answered, 0) / expected_answers
            if expected_answers else 0
        )
        if absolute_deficit < 10 and relative_deficit < 10:
            continue
        score = confidence * (absolute_deficit * 0.55 + relative_deficit * 0.65)
        score += shortage * 20
        if relative_deficit >= 10:
            reason = "他分野より正答率が低い"
        elif absolute_deficit >= 10:
            reason = "正答率が低い"
        else:
            reason = "正答率が低い"
        candidates.append(_weak_item(item, score, reason))

    if broad_enough:
        low_engagement = [
            item for item in fields
            if 0 < item["answered_count"] < MIN_RELIABLE_ANSWERS
        ]
        for item in low_engagement:
            shortage = 1 - (item["answered_count"] / max(expected_answers, 1))
            candidates.append(_weak_item(item, 22 + shortage * 18, "取り組み不足"))

        # 未学習だけでTOP3を占有しないよう、代表の1分野だけ候補にする。
        unlearned = [item for item in fields if item["answered_count"] == 0]
        if unlearned:
            candidates.append(_weak_item(unlearned[0], 28, "未学習"))

    return sorted(
        candidates,
        key=lambda item: (-item["priority_score"], item["category_small"]),
    )


def _weak_item(item: dict[str, Any], priority_score: float, reason: str) -> dict[str, Any]:
    return {
        "category_small": item["category_small"],
        "name": item["name"],
        "score": item["accuracy"] if item["accuracy"] is not None else 0,
        "answers": item["answered_count"],
        "reason": reason,
        "priority_score": round(priority_score, 3),
    }


def build_learning_guidance(
    total_answers: int,
    fields: list[dict[str, Any]],
) -> dict[str, Any]:
    """TOP用の苦手TOP3・おすすめ分野・分析段階を返す。"""
    if total_answers < FOUNDATION_ANSWER_THRESHOLD:
        recommended = _foundation_recommendation(fields)
        recommended_study = [(recommended["name"], 10)] if recommended else []
        recommended_reason = None
        if recommended:
            reason = (
                "未学習" if recommended["answered_count"] == 0
                else "取り組み不足"
                if recommended["answered_count"] < MIN_RELIABLE_ANSWERS
                else None
            )
            recommended_reason = build_recommendation_reason(
                recommended["name"], 10, reason,
            )
        return {
            "phase": "foundation",
            "weak_fields": [],
            "weak_analysis_message": (
                "まずは100問を目標に基礎を固めましょう。"
                "100問を超えると、あなたの苦手傾向を詳しく分析します。"
            ),
            "recommended_study": recommended_study,
            "recommendation_reason": recommended_reason,
        }

    weak_fields = _weakness_candidates(fields)[:3]
    recommended_name = weak_fields[0]["name"] if weak_fields else None
    recommended_study = [(recommended_name, 10)] if recommended_name else []
    return {
        "phase": "analysis",
        "weak_fields": weak_fields,
        "weak_analysis_message": (
            "分野別の分析に必要な履歴がまだ足りません。"
            if not weak_fields else ""
        ),
        "recommended_study": recommended_study,
        "recommendation_reason": (
            build_recommendation_reason(
                recommended_name,
                10,
                weak_fields[0]["reason"],
            )
            if recommended_name else None
        ),
    }


def build_gensan_comment(
    total_answers: int,
    fields: list[dict[str, Any]],
    weak_fields: list[dict[str, Any]],
    recommended_study: list[tuple[str, int]],
    streak_days: int = 0,
    today_progress: int = 0,
) -> str:
    """保存済み学習データから「褒める＋次の一歩」を決定的に作る。"""
    learned = [item for item in fields if item["answered_count"] > 0]
    if not learned:
        return "まだ始まったばかりだな＾＾\nまずは5問だけやってみるか？"

    praise_item = max(
        learned,
        key=lambda item: (
            item["accuracy"] if item["accuracy"] is not None else -1,
            item["answered_count"],
            -item["category_small"],
        ),
    )
    next_name = recommended_study[0][0] if recommended_study else None
    if not next_name and weak_fields:
        next_name = weak_fields[0]["name"]
    if not next_name:
        alternatives = [
            item for item in fields
            if item["name"] != praise_item["name"]
        ]
        if alternatives:
            next_name = min(
                alternatives,
                key=lambda item: (item["answered_count"], item["category_small"]),
            )["name"]
    if not next_name:
        return f"{praise_item['name']}、いい感じだぞ＾＾\n今日もおすすめ問題を5問だけいってみるか？"

    template_index = (
        total_answers + streak_days + today_progress
        + sum(ord(char) for char in praise_item["name"] + next_name)
    ) % len(GENSAN_FEEDBACK_TEMPLATES)
    return GENSAN_FEEDBACK_TEMPLATES[template_index].format(
        praise=praise_item["name"],
        next=next_name,
    )
