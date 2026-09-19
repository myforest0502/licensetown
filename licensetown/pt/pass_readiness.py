"""LicenseTown internal pass-readiness evaluator v0.1.

This is an evidence-gated status machine, not a pass probability. It is pure,
read-only, shadow/diagnostic logic. Learner-facing wording belongs elsewhere.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Iterable, Mapping

from field_evidence import build_field_evidence
from field_progress import build_field_progress
from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_weakness_evidence import (
    CROSS_QUESTION_CONFIDENT_WRONG,
    CROSS_QUESTION_WRONG,
    REPEATED_SAME_QUESTION_WRONG,
)
from phase11_formal_judgment import build_formal_context
from question_bank import get_question_tag, question_ids


VERSION = "lt_pass_readiness_v0.1"
ABILITIES = ("KNOW", "MEASURE", "INTERPRET", "PREDICT", "PRESCRIBE", "DECIDE")

# Evidence-sufficiency gates, intentionally named rather than combined into a score.
# v0.1 rationale: the current Production-shaped learner has hundreds of attempts
# and roughly one quarter of canonical Nodes touched, which is enough to distinguish
# active repair from mere first exposure, but nowhere near broad syllabus readiness.
MIN_ASSESSABLE_EVALUABLE_ATTEMPTS = 100
MIN_ASSESSABLE_NODE_COVERAGE = 0.20
MATERIAL_ACTIVE_REPAIR_NODES = 3
BROAD_NODE_COVERAGE = 0.60
STRONG_NODE_COVERAGE = 0.80
BROAD_ABILITY_COVERAGE = 0.40
STRONG_ABILITY_COVERAGE = 0.60
MEANINGFUL_REPAIRED_NODES = 10
MEANINGFUL_STABLE_NODES = 20
STRONG_STABLE_NODES = 50
RETENTION_STABLE_SHARE = 0.50
STRONG_RETENTION_STABLE_SHARE = 0.70

REPEATED_LEVELS = {
    REPEATED_SAME_QUESTION_WRONG,
    CROSS_QUESTION_WRONG,
    CROSS_QUESTION_CONFIDENT_WRONG,
}


def _ability_catalog() -> dict[str, set[str]]:
    opportunities: dict[str, set[str]] = {ability: set() for ability in ABILITIES}
    for question_id in question_ids():
        tag = get_question_tag(question_id)
        ability = str(tag.get("primary_ability") or "").strip().upper()
        if ability not in opportunities:
            continue
        node_id = canonicalize_knowledge_node_id(str(tag.get("knowledge_node_id") or ""))
        if node_id:
            opportunities[ability].add(node_id)
    return opportunities


_ABILITY_OPPORTUNITIES = _ability_catalog()


def _reason(code: str, **facts: Any) -> dict[str, Any]:
    return {"code": code, "facts": facts}


def _trial100_component(records: Iterable[Mapping[str, Any]] | None) -> dict[str, Any]:
    records = [dict(item) for item in (records or [])]
    timed = [item for item in records if item.get("timed_full_format") is True]
    supportive = [item for item in timed if item.get("supportive") is True]
    return {
        "record_count": len(records),
        "timed_full_format_count": len(timed),
        "supportive_timed_count": len(supportive),
        "has_supportive_full_format_evidence": bool(supportive),
        "status": (
            "missing" if not records
            else "supportive" if supportive
            else "recorded_not_yet_supportive"
        ),
    }


def _activity_component(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    days = set()
    for item in attempts:
        value = item.get("answered_at") or item.get("attempted_at")
        if isinstance(value, datetime):
            days.add(value.date().isoformat())
        elif value:
            days.add(str(value)[:10])
    return {
        "attempt_count": len(attempts),
        "active_day_count": len(days),
        "mastery_credit_applied": False,
    }


def _ability_components(
    evidence: Mapping[str, Any],
    active_by_node: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    states = {
        str(item["canonical_node_id"]): str(item["state"])
        for item in evidence.get("canonical_node_evidence", [])
    }
    result: dict[str, dict[str, Any]] = {}
    for ability in ABILITIES:
        nodes = _ABILITY_OPPORTUNITIES[ability]
        touched = {node for node in nodes if states.get(node, "unseen") != "unseen"}
        state_counts = Counter(states.get(node, "unseen") for node in nodes)
        active_weak = {
            node for node in nodes
            if node in active_by_node
            and int(active_by_node[node].get("active_evaluable_wrong_attempt_count") or 0) > 0
        }
        total = len(nodes)
        result[ability] = {
            "opportunity_canonical_nodes": total,
            "touched_canonical_nodes": len(touched),
            "coverage": len(touched) / total if total else 0.0,
            "state_counts": dict(sorted(state_counts.items())),
            "repaired_or_stable_nodes": state_counts["repaired"] + state_counts["stable"],
            "stable_nodes": state_counts["stable"],
            "active_weakness_nodes": len(active_weak),
        }
    return result


def _repair_component(
    evidence: Mapping[str, Any],
    active_by_node: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    repairing = sum(
        int(field.get("repairing_node_count") or 0)
        for field in evidence.get("fields", [])
    )
    active_wrong_nodes = 0
    active_confident_wrong_nodes = 0
    active_repeated_nodes = 0
    for item in active_by_node.values():
        if int(item.get("active_evaluable_wrong_attempt_count") or 0) > 0:
            active_wrong_nodes += 1
        if item.get("active_has_confident_wrong"):
            active_confident_wrong_nodes += 1
        if item.get("active_weakness_evidence_level") in REPEATED_LEVELS:
            active_repeated_nodes += 1
    return {
        "field_membership_repairing_count": repairing,
        "active_wrong_node_count": active_wrong_nodes,
        "active_confident_wrong_node_count": active_confident_wrong_nodes,
        "active_repeated_weakness_node_count": active_repeated_nodes,
        "material_active_repair": (
            active_wrong_nodes >= MATERIAL_ACTIVE_REPAIR_NODES
            or active_confident_wrong_nodes >= 2
            or active_repeated_nodes >= 2
        ),
    }


def _retention_component(evidence: Mapping[str, Any]) -> dict[str, Any]:
    counts = Counter(
        str(item.get("state") or "unseen")
        for item in evidence.get("canonical_node_evidence", [])
    )
    repaired = counts["repaired"]
    due = counts["recheck_due"]
    stable = counts["stable"]
    retention_known = repaired + due + stable
    stable_share = stable / retention_known if retention_known else 0.0
    return {
        "repaired_nodes": repaired,
        "recheck_due_nodes": due,
        "stable_nodes": stable,
        "retention_known_nodes": retention_known,
        "stable_share": stable_share,
        "meaningful_short_term_repair": repaired >= MEANINGFUL_REPAIRED_NODES,
        "meaningful_stable_evidence": stable >= MEANINGFUL_STABLE_NODES,
        "strong_stable_evidence": stable >= STRONG_STABLE_NODES,
    }


def build_pass_readiness(
    attempts: Iterable[dict[str, Any]],
    field_evidence: Mapping[str, Any] | None = None,
    progress: Mapping[str, Any] | None = None,
    trial100_records: Iterable[Mapping[str, Any]] | None = None,
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Return deterministic internal readiness status and inspectable evidence."""
    attempts = [dict(item) for item in attempts]
    evidence = dict(field_evidence or build_field_evidence(attempts, as_of=as_of))
    progress = dict(progress or build_field_progress(evidence))
    context = build_formal_context(attempts, evidence, as_of=as_of)
    active_by_node = context["active_by_node"]

    overall = dict(progress["overall"])
    total_nodes = int(overall["total_unique_canonical_nodes"])
    touched_nodes = int(overall["touched_unique_canonical_nodes"])
    coverage = touched_nodes / total_nodes if total_nodes else 0.0
    evaluable_attempts = sum(
        int(field.get("evaluable_answer_count") or 0)
        for field in evidence.get("fields", [])
    )
    state_counts = Counter(overall.get("state_counts") or {})

    critical_nodes = set(context.get("active_by_node", {})) & set(
        context.get("active_field_facts", {}).get("critical_nodes", set())
    )
    # build_formal_context stores Critical membership in module catalog, not active_field_facts.
    # Reconstruct current active Critical nodes from the same canonical bank contract.
    from phase11_formal_judgment import _CATALOG as formal_catalog
    critical_nodes = {
        node for node, item in active_by_node.items()
        if node in formal_catalog["critical_nodes"]
        and int(item.get("active_evaluable_wrong_attempt_count") or 0) > 0
    }

    repair = _repair_component(evidence, active_by_node)
    retention = _retention_component(evidence)
    ability = _ability_components(evidence, active_by_node)
    trial100 = _trial100_component(trial100_records)
    activity = _activity_component(attempts)

    ability_coverages = [item["coverage"] for item in ability.values() if item["opportunity_canonical_nodes"]]
    min_ability_coverage = min(ability_coverages, default=0.0)
    under_broad_abilities = [
        name for name, item in ability.items()
        if item["opportunity_canonical_nodes"] and item["coverage"] < BROAD_ABILITY_COVERAGE
    ]
    under_strong_abilities = [
        name for name, item in ability.items()
        if item["opportunity_canonical_nodes"] and item["coverage"] < STRONG_ABILITY_COVERAGE
    ]

    blocking: list[dict[str, Any]] = []
    caution: list[dict[str, Any]] = []
    positive: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []

    if not trial100["record_count"]:
        missing.append(_reason("trial100_not_recorded"))
    elif trial100["has_supportive_full_format_evidence"]:
        positive.append(_reason("supportive_trial100_full_format", count=trial100["supportive_timed_count"]))
    else:
        caution.append(_reason("trial100_recorded_not_yet_supportive", count=trial100["record_count"]))

    if coverage >= BROAD_NODE_COVERAGE:
        positive.append(_reason("broad_syllabus_coverage", coverage=coverage))
    if retention["meaningful_stable_evidence"]:
        positive.append(_reason("meaningful_stable_nodes", stable_nodes=retention["stable_nodes"]))
    if not critical_nodes:
        positive.append(_reason("no_active_critical_safety_blocker"))

    assessable = (
        evaluable_attempts >= MIN_ASSESSABLE_EVALUABLE_ATTEMPTS
        and coverage >= MIN_ASSESSABLE_NODE_COVERAGE
    )
    if not assessable:
        status = "insufficient_evidence"
        blocking.append(_reason(
            "readiness_evidence_too_sparse",
            evaluable_attempts=evaluable_attempts,
            minimum_evaluable_attempts=MIN_ASSESSABLE_EVALUABLE_ATTEMPTS,
            node_coverage=coverage,
            minimum_node_coverage=MIN_ASSESSABLE_NODE_COVERAGE,
        ))
    elif critical_nodes:
        status = "safety_attention_required"
        blocking.append(_reason("active_critical_safety_wrong", active_critical_nodes=len(critical_nodes)))
    elif repair["material_active_repair"]:
        status = "repair_required"
        blocking.append(_reason(
            "material_active_repair_burden",
            active_wrong_nodes=repair["active_wrong_node_count"],
            active_confident_wrong_nodes=repair["active_confident_wrong_node_count"],
            active_repeated_nodes=repair["active_repeated_weakness_node_count"],
        ))
    elif (
        retention["recheck_due_nodes"] > 0
        or (
            retention["meaningful_short_term_repair"]
            and retention["stable_share"] < RETENTION_STABLE_SHARE
        )
    ):
        status = "retention_confirmation_needed"
        caution.append(_reason(
            "retention_not_yet_confirmed",
            repaired_nodes=retention["repaired_nodes"],
            recheck_due_nodes=retention["recheck_due_nodes"],
            stable_nodes=retention["stable_nodes"],
            stable_share=retention["stable_share"],
        ))
    elif coverage < BROAD_NODE_COVERAGE or under_broad_abilities:
        status = "building_coverage"
        caution.append(_reason(
            "coverage_or_ability_blind_spot",
            node_coverage=coverage,
            minimum_broad_node_coverage=BROAD_NODE_COVERAGE,
            under_broad_abilities=under_broad_abilities,
        ))
    else:
        strong_ready = (
            coverage >= STRONG_NODE_COVERAGE
            and not under_strong_abilities
            and retention["strong_stable_evidence"]
            and retention["stable_share"] >= STRONG_RETENTION_STABLE_SHARE
            and trial100["has_supportive_full_format_evidence"]
        )
        if strong_ready:
            status = "readiness_supported"
            positive.append(_reason(
                "broad_consistent_readiness_evidence",
                node_coverage=coverage,
                min_ability_coverage=min_ability_coverage,
                stable_nodes=retention["stable_nodes"],
                stable_share=retention["stable_share"],
            ))
        else:
            status = "approaching_readiness"
            caution.append(_reason(
                "highest_readiness_evidence_not_yet_complete",
                strong_node_coverage_met=coverage >= STRONG_NODE_COVERAGE,
                under_strong_abilities=under_strong_abilities,
                strong_stable_evidence=retention["strong_stable_evidence"],
                stable_share=retention["stable_share"],
                supportive_trial100=trial100["has_supportive_full_format_evidence"],
            ))

    components = {
        "coverage": {
            "total_unique_canonical_nodes": total_nodes,
            "touched_unique_canonical_nodes": touched_nodes,
            "node_coverage": coverage,
            "evaluable_attempts": evaluable_attempts,
        },
        "node_stability": {
            "state_counts": dict(state_counts),
            "overall_progress_score": overall.get("overall_progress_score"),
        },
        "repair_burden": repair,
        "retention": retention,
        "safety": {
            "active_critical_wrong_node_count": len(critical_nodes),
            "ready": not critical_nodes,
        },
        "confidence_errors": {
            "active_confident_wrong_node_count": repair["active_confident_wrong_node_count"],
            "active_repeated_weakness_node_count": repair["active_repeated_weakness_node_count"],
        },
        "ability_domains": ability,
        "trial100": trial100,
        "activity_context": activity,
    }
    return {
        "version": VERSION,
        "status": status,
        "shadow_only": True,
        "pass_probability": None,
        "pass_guarantee": False,
        "authoritative_attempt_source": "question_attempts",
        "authoritative_node_state_source": "pure_derive_all_user_node_states",
        "blocking_reasons": blocking,
        "caution_reasons": caution,
        "positive_evidence": positive,
        "missing_evidence": missing,
        "components": components,
        "thresholds": {
            "minimum_assessable_evaluable_attempts": MIN_ASSESSABLE_EVALUABLE_ATTEMPTS,
            "minimum_assessable_node_coverage": MIN_ASSESSABLE_NODE_COVERAGE,
            "material_active_repair_nodes": MATERIAL_ACTIVE_REPAIR_NODES,
            "broad_node_coverage": BROAD_NODE_COVERAGE,
            "strong_node_coverage": STRONG_NODE_COVERAGE,
            "broad_ability_coverage": BROAD_ABILITY_COVERAGE,
            "strong_ability_coverage": STRONG_ABILITY_COVERAGE,
            "meaningful_repaired_nodes": MEANINGFUL_REPAIRED_NODES,
            "meaningful_stable_nodes": MEANINGFUL_STABLE_NODES,
            "strong_stable_nodes": STRONG_STABLE_NODES,
            "retention_stable_share": RETENTION_STABLE_SHARE,
            "strong_retention_stable_share": STRONG_RETENTION_STABLE_SHARE,
        },
    }
