"""Plain-language learner navigation built from validated deterministic evidence."""

from __future__ import annotations

from typing import Any, Mapping


STATUS_COPY = {
    "insufficient_evidence": (
        "まだ現在地を測っている途中",
        "まずは学習データを増やして、確認できた範囲を広げていこう。",
    ),
    "safety_attention_required": (
        "まず大事なところを確認しよう",
        "安全に関わる重要な内容から先に確認する段階です。",
    ),
    "repair_required": (
        "今は苦手を直している途中",
        "間違えた内容を直すことが、今いちばん効果の高い学習です。",
    ),
    "retention_confirmation_needed": (
        "一度できた内容を、時間を空けて確認しよう",
        "できた直後だけでなく、時間を空けても答えられるか確かめる段階です。",
    ),
    "building_coverage": (
        "まだ見ていない範囲を広げよう",
        "弱点だけでなく、まだ十分に確認できていない分野を増やしていこう。",
    ),
    "approaching_readiness": (
        "かなり整ってきた。残りを確認しよう",
        "できている範囲が増えています。残る確認を一つずつ仕上げよう。",
    ),
    "readiness_supported": (
        "今の学習データでは、合格に必要な力が整ってきている",
        "本番形式の確認も続けながら、今の力を維持していこう。",
    ),
}

REASON_COPY = {
    "safety_repair": "安全に関わる重要な内容を先に確認しよう。",
    "confident_wrong_repair": "自信を持って間違えた内容を優先して直そう。",
    "repeated_wrong_repair": "繰り返し間違えている内容を先に直そう。",
    "repairing_continue": "今直している内容を、もう一段確かめよう。",
    "retention_recheck": "一度できた内容を、時間を空けてもう一度確認しよう。",
    "low_progress_repair": "確認できた範囲の中で、まだ仕上げが必要な内容を進めよう。",
    "coverage_expand": "まだ確認が足りない分野を広げよう。",
    "stable_maintain": "今の力を保ちながら、広く確認を続けよう。",
}

ATTENTION_LABELS = {
    "safety_repair": "大事な確認",
    "confident_wrong_repair": "優先して直す",
    "repeated_wrong_repair": "繰り返し確認",
    "repairing_continue": "修復中",
    "retention_recheck": "再確認の時期",
    "low_progress_repair": "仕上げ中",
    "coverage_expand": "まだ確認が足りない",
}


def _stable_areas(shadow: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for field in shadow.get("fields", []):
        counts = field.get("state_counts") or {}
        stable = int(counts.get("stable") or 0)
        if stable:
            rows.append({
                "field": field["field_name"],
                "stable_count": stable,
                "message": f"時間を空けても確認できた内容が{stable}個あります。",
            })
    return sorted(rows, key=lambda item: (-item["stable_count"], item["field"]))[:3]


def _repair_areas(shadow: Mapping[str, Any]) -> list[dict[str, Any]]:
    result = []
    for item in shadow.get("weakness_top3", []):
        if not item.get("is_proven_weakness"):
            continue
        result.append({
            "field": item["field_name"],
            "label": ATTENTION_LABELS.get(item["reason_code"], "確認中"),
            "message": REASON_COPY.get(item["reason_code"], "もう一度確認しよう。"),
        })
    return result[:3]


def _coverage_gaps(shadow: Mapping[str, Any], repair_fields: set[str]) -> list[dict[str, Any]]:
    rows = []
    for field in shadow.get("fields", []):
        name = str(field["field_name"])
        if name in repair_fields:
            continue
        rows.append({
            "field": name,
            "coverage": float(field.get("node_coverage") or 0.0),
            "message": "まだ確認できていない内容があります。弱いと決まったわけではありません。",
        })
    return sorted(rows, key=lambda item: (item["coverage"], item["field"]))[:3]


def build_learner_readiness_presentation(
    readiness: Mapping[str, Any],
    shadow: Mapping[str, Any],
) -> dict[str, Any]:
    status = str(readiness.get("status") or "insufficient_evidence")
    headline, summary = STATUS_COPY.get(status, STATUS_COPY["insufficient_evidence"])
    recommendation = dict(shadow.get("recommendation_intent") or {})
    reason_code = str(recommendation.get("priority_reason") or "coverage_expand")
    target_field = recommendation.get("target_field")
    count = int(recommendation.get("requested_question_count") or 10)
    learning_intent = str(recommendation.get("learning_intent") or "exploration")

    attention = []
    for item in shadow.get("weakness_top3", [])[:3]:
        code = str(item.get("reason_code") or "coverage_expand")
        attention.append({
            "field": item.get("field_name"),
            "label": ATTENTION_LABELS.get(code, "確認中"),
            "message": REASON_COPY.get(code, "もう一度確認しよう。"),
            "proven_weakness": bool(item.get("is_proven_weakness")),
        })

    repair_areas = _repair_areas(shadow)
    repair_fields = {item["field"] for item in repair_areas}
    retention = dict((readiness.get("components") or {}).get("retention") or {})
    trial100 = dict((readiness.get("components") or {}).get("trial100") or {})
    safety = dict((readiness.get("components") or {}).get("safety") or {})

    if int(retention.get("recheck_due_nodes") or 0) > 0:
        retention_message = "時間を空けて再確認する内容があります。"
    elif int(retention.get("repaired_nodes") or 0) > 0:
        retention_message = "いったん修復できた内容があります。次は時間を空けた確認です。"
    elif int(retention.get("stable_nodes") or 0) > 0:
        retention_message = "時間を空けても確認できた内容があります。"
    else:
        retention_message = "時間を空けた再確認の記録は、これから増えていきます。"

    trial_message = (
        "本番形式の確認でも手応えが記録されています。"
        if trial100.get("has_supportive_full_format_evidence")
        else "本番形式の確認はまだ十分に記録されていません。"
    )

    return {
        "headline": headline,
        "summary": summary,
        "today_action": {
            "field": target_field,
            "count": count,
            "learning_intent": learning_intent,
            "reason_code": reason_code,
            "reason": REASON_COPY.get(reason_code, "今日のおすすめから進めよう。"),
            "button_label": "今日の学習を始める",
        },
        "attention_items": attention,
        "stable_areas": _stable_areas(shadow),
        "repair_areas": repair_areas,
        "coverage_gaps": _coverage_gaps(shadow, repair_fields),
        "retention_message": retention_message,
        "trial100_message": trial_message,
        "safety_attention": not bool(safety.get("ready", True)),
        "trace": {
            "readiness_status": status,
            "recommendation_reason_code": reason_code,
            "readiness_version": readiness.get("version"),
            "dashboard_shadow_status": shadow.get("status"),
        },
    }
