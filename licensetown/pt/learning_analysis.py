"""学習履歴から優先課題と今日のおすすめを決定論的に選ぶ。"""

from __future__ import annotations

from typing import Any

from question_bank import BASIC_CATEGORY_SMALLS


FOUNDATION_ANSWER_THRESHOLD = 100
MIN_RELIABLE_ANSWERS = 10
TARGET_FIELD_ACCURACY = 70

# 十分な回答数がある分野だけを「得意・頑張った分野」として扱う。
# 1問100%のような偶然性が大きい数字は、源さんが褒め材料に使わない。
GENSAN_FEEDBACK_TEMPLATES = (
    "{praise}は{answers}問まで積んで正答率{accuracy}%だ。ちゃんと力になってるぞ＾＾\n今日は{next}を5問、丁寧にいってみるか。",
    "{praise}は{answers}問やって正答率{accuracy}%。ここまで積んだのは立派だ＾＾\n次は{next}を少しずつ詰めよう。",
    "{praise}は{answers}問まで続けて正答率{accuracy}%だな。積み重ねはちゃんと見えてるぞ＾＾\n今日は{next}を5問やってみるか。",
    "{praise}は{answers}問で正答率{accuracy}%。一問二問の数字じゃない、これは積み上げた結果だ＾＾\n次は{next}を少し触っておこう。",
    "{praise}は{answers}問やって正答率{accuracy}%まで来たな＾＾\n今度は{next}を5問、焦らず固めていこう。",
)


def build_recommendation_reason(
    field_name: str,
    question_count: int,
    reason: str | None,
) -> str:
    """既存の優先課題理由を、おすすめ学習用の短い説明に変換する。"""
    if reason == "取り組み不足":
        return (
            "まだ回答数が少なく、実力判定のデータが足りません。"
            f"まず{question_count}問取り組んで傾向を確認してみよう。"
        )
    if reason == "正答率が低い":
        return (
            f"{field_name}は現在の正答率が70%未満で、優先して確認したい分野です。"
            f"{question_count}問取り組んで理解を固めてみよう。"
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
    """Return lightweight priority candidates while preserving reason semantics.

    `weak_fields` is retained as a compatibility key for callers, but these rows
    are learner/supporter priorities, not all proven weaknesses. Reliable
    performance below the visible 70% target comes first. Once learning is broad
    enough, low-sample and unlearned fields can fill remaining priority slots.
    """
    detailed_answers = sum(item["answered_count"] for item in fields)
    learned_fields = [item for item in fields if item["answered_count"] > 0]
    broad_enough = detailed_answers >= 60 and len(learned_fields) >= 6
    candidates = []

    for item in fields:
        answered = item["answered_count"]
        accuracy = item["accuracy"]
        if answered < MIN_RELIABLE_ANSWERS or accuracy is None:
            continue
        if accuracy >= TARGET_FIELD_ACCURACY:
            continue
        # Demonstrated below-target performance outranks coverage-only gaps.
        # Lower accuracy ranks first; answer volume only breaks close ties.
        score = 300 + (TARGET_FIELD_ACCURACY - accuracy) + min(answered, 100) / 100
        candidates.append(_weak_item(item, score, "正答率が低い"))

    if broad_enough:
        for item in fields:
            answered = item["answered_count"]
            if 0 < answered < MIN_RELIABLE_ANSWERS:
                score = 200 + (MIN_RELIABLE_ANSWERS - answered) / MIN_RELIABLE_ANSWERS
                candidates.append(_weak_item(item, score, "取り組み不足"))

        # Unlearned fields are not called weak; they are coverage priorities.
        # Include all of them so TOP3 can be filled deterministically as higher
        # priority demonstrated/low-sample gaps are resolved.
        for item in fields:
            if item["answered_count"] == 0:
                candidates.append(_weak_item(item, 100, "未学習"))

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
    """TOP用の優先課題TOP3・おすすめ分野・分析段階を返す。"""
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
                "100問を超えると、次に優先したい分野を詳しく分析します。"
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
            "分野別の優先課題を決めるための履歴がまだ足りません。"
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


def _field_by_name(fields: list[dict[str, Any]], name: str | None) -> dict[str, Any] | None:
    if not name:
        return None
    return next((item for item in fields if item.get("name") == name), None)


def _next_field_name(
    fields: list[dict[str, Any]],
    weak_fields: list[dict[str, Any]],
    recommended_study: list[tuple[str, int]],
    exclude_name: str | None = None,
) -> str | None:
    if recommended_study:
        return recommended_study[0][0]
    if weak_fields:
        return weak_fields[0]["name"]
    alternatives = [item for item in fields if item.get("name") != exclude_name]
    if alternatives:
        return min(
            alternatives,
            key=lambda item: (item["answered_count"], item["category_small"]),
        )["name"]
    return None


def build_gensan_comment(
    total_answers: int,
    fields: list[dict[str, Any]],
    weak_fields: list[dict[str, Any]],
    recommended_study: list[tuple[str, int]],
    streak_days: int = 0,
    today_progress: int = 0,
) -> str:
    """保存済み学習データから、根拠のある「見守り＋次の一歩」を作る。

    源さんは正答率だけでは褒めない。回答数が10問未満の分野はまだ
    得意・不得意を断定せず、継続日数・回答量・十分な標本がある分野の
    実績を優先して言葉にする。
    """
    learned = [item for item in fields if item["answered_count"] > 0]
    if not learned:
        return "まだ始まったばかりだな＾＾\nまずは5問だけやってみるか？"

    reliable = [
        item for item in learned
        if item["answered_count"] >= MIN_RELIABLE_ANSWERS
        and item["accuracy"] is not None
    ]
    strengths = [item for item in reliable if item["accuracy"] >= TARGET_FIELD_ACCURACY]

    # 少数回答の高正答率は「褒める根拠」ではなく「まだ判断が早い数字」。
    low_sample_high = [
        item for item in learned
        if item["answered_count"] < MIN_RELIABLE_ANSWERS
        and item["accuracy"] is not None
        and item["accuracy"] >= TARGET_FIELD_ACCURACY
    ]
    low_sample_item = max(
        low_sample_high,
        key=lambda item: (item["accuracy"], item["answered_count"], -item["category_small"]),
        default=None,
    )

    praise_item = max(
        strengths,
        # 「正答率100%の10問」より、十分な量を積み上げた分野を優先する。
        key=lambda item: (item["answered_count"], item["accuracy"], -item["category_small"]),
        default=None,
    )
    next_name = _next_field_name(
        fields,
        weak_fields,
        recommended_study,
        exclude_name=praise_item["name"] if praise_item else None,
    )
    next_item = _field_by_name(fields, next_name)

    lines: list[str] = []

    if streak_days >= 7:
        lines.append(f"{streak_days}日続けてるの、ちゃんと見てるぞ＾＾ これは立派だ。")
    elif streak_days >= 3:
        lines.append(f"{streak_days}日続いてるな。こういう積み重ねが一番強いぞ＾＾")

    if praise_item:
        if not lines:
            template_index = (
                total_answers + streak_days + today_progress
                + sum(ord(char) for char in praise_item["name"] + (next_name or ""))
            ) % len(GENSAN_FEEDBACK_TEMPLATES)
            if next_name:
                return GENSAN_FEEDBACK_TEMPLATES[template_index].format(
                    praise=praise_item["name"],
                    answers=praise_item["answered_count"],
                    accuracy=praise_item["accuracy"],
                    next=next_name,
                )
            return (
                f"{praise_item['name']}は{praise_item['answered_count']}問まで積んで"
                f"正答率{praise_item['accuracy']}%。ちゃんと力になってるぞ＾＾\n"
                "今日もおすすめ問題を5問だけいってみるか？"
            )
        lines.append(
            f"{praise_item['name']}も{praise_item['answered_count']}問やって"
            f"正答率{praise_item['accuracy']}%。積み上げた結果が出てる。"
        )
    elif low_sample_item:
        count = low_sample_item["answered_count"]
        counter = "1問" if count == 1 else f"{count}問"
        lines.append(
            f"{low_sample_item['name']}は{counter}で正答率{low_sample_item['accuracy']}%。"
            "数字はいいけど、まだ『得意』と決めるには早いぞ。"
        )
    elif not lines:
        lines.append(
            f"ここまで{total_answers}問やってきたな。正答率だけじゃなく、"
            "続けて積むところまでちゃんと見てるぞ＾＾"
        )

    if next_name:
        if next_item and next_item.get("answered_count", 0) >= MIN_RELIABLE_ANSWERS:
            accuracy = next_item.get("accuracy")
            if accuracy is not None and accuracy < TARGET_FIELD_ACCURACY:
                lines.append(
                    f"今は{next_name}が{next_item['answered_count']}問で正答率{accuracy}%。"
                    "ここは逃げずに、今日はまず5問だけ丁寧に詰めよう。"
                )
            else:
                lines.append(f"今日は{next_name}を5問だけやって、もう少し様子を見よう。")
        elif next_item and next_item.get("answered_count", 0) > 0:
            lines.append(
                f"{next_name}はまだ{next_item['answered_count']}問だけだ。"
                "今日は5問足して、判断できる材料を増やそう。"
            )
        else:
            lines.append(f"今日は{next_name}をまず5問。手をつけて今の力を見てみよう。")
    else:
        lines.append("今日はおすすめ問題を5問だけ。焦らず続けりゃ大丈夫だ＾＾")

    return "\n".join(lines)
