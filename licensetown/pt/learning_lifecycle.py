"""Pure, provisional PT lifecycle diagnostics; no runtime selection authority."""
from collections import Counter


VERSION = "pt_learning_lifecycle_v0.1"


def build_learning_lifecycle(
    evidence_bundle, target_bundle, node_states, *,
    critical_safety_unresolved_count=None,
):
    """Interpret aligned, single-learner snapshots at one caller-chosen as_of.

    Inputs are build_field_evidence/build_field_targets outputs and the complete
    derive_all_user_node_states output. No history replay or time calculation is
    performed here. A missing Safety count means unavailable, never safe.
    """
    def count(value):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("snapshot counts must be non-negative integers")
        return value

    def fields(bundle):
        rows = list(bundle["fields"])
        indexed = {count(row["field_id"]): row for row in rows}
        if len(indexed) != len(rows) or set(indexed) != set(range(1, 19)):
            raise ValueError("exactly one row per PT field 1-18 is required")
        return indexed

    evidence, targets = fields(evidence_bundle), fields(target_bundle)
    checkpoints = []
    for field_id in range(1, 19):
        row, target = evidence[field_id], targets[field_id]
        supply = count(row["total_question_count"])
        total_nodes = count(row["total_canonical_node_count"])
        if (supply != count(target["total_question_count"])
                or total_nodes != count(target["total_canonical_nodes"])):
            raise ValueError("field supply snapshots must match")
        minimum = count(target["minimum_initial_questions"])
        spread = count(target["minimum_node_spread"])
        touched = count(row["attempted_canonical_node_count"])
        unique = count(row["answered_unique_question_count"])
        answers = count(row["evaluable_answer_count"])
        if touched > total_nodes or unique > supply or total_nodes > supply:
            raise ValueError("observed coverage exceeds catalog supply")
        if supply and not (0 < minimum <= supply and 0 < spread <= total_nodes):
            raise ValueError("supplied fields require positive attainable targets")
        reached = bool(supply and answers >= minimum and unique >= minimum and touched >= spread)
        checkpoints.append({"field_id": field_id, "has_supply": bool(supply),
                            "checkpoint_reached": reached})

    nodes = list(node_states)
    indexed_nodes = {row["canonical_node_id"]: row for row in nodes}
    if len(indexed_nodes) != len(nodes) or any(not key for key in indexed_nodes):
        raise ValueError("formal Node snapshots must have unique nonempty IDs")
    counts = Counter(row["state"] for row in nodes)
    if set(counts) - {"unseen", "checking", "repairing", "repaired", "recheck_due", "stable"}:
        raise ValueError("unknown formal Node state")
    # Check overlapping catalog identities without summing multi-field memberships.
    # Formal equivalence-derived Nodes outside that catalog remain in node_states.
    for row in evidence_bundle["canonical_node_evidence"]:
        formal = indexed_nodes.get(row["canonical_node_id"])
        if row["state"] != (formal["state"] if formal else "unseen"):
            raise ValueError("field evidence and formal Node states must match")

    missing = []
    safety = critical_safety_unresolved_count
    if safety is None:
        missing.append("critical_safety_unresolved_count")
    else:
        safety = count(safety)
    supplied = [row for row in checkpoints if row["has_supply"]]
    coverage = bool(supplied) and all(row["checkpoint_reached"] for row in supplied)
    repair = bool(counts["repairing"] or (safety is not None and safety > 0))
    due = counts["recheck_due"]
    scheduled = sum(row["state"] in {"repaired", "stable"}
                    and row.get("retention_checkpoint") in {"day3", "day7", "day30"}
                    for row in nodes)
    durable = sum(row["state"] == "stable" and row.get("retention_stage") == "durable"
                  for row in nodes)
    # Due work may take priority before broad coverage. Future/durable work alone
    # does not displace initial coverage, and unresolved checking still needs depth.
    retention = bool(not repair and (due or (
        coverage and not counts["checking"] and (scheduled or durable)
    )))
    reasons = ["initial_coverage_checkpoint_reached" if coverage else "initial_coverage_incomplete"]
    if not supplied:
        reasons.append("no_field_supply")
    if counts["repairing"]:
        reasons.append("current_repairing")
    if safety is not None and safety > 0:
        reasons.append("critical_safety_unresolved")
    if safety is None:
        reasons.append("safety_evidence_unavailable")
    if due:
        reasons.append("formal_retention_due")
    if scheduled:
        reasons.append("formal_retention_scheduled")
    if durable:
        reasons.append("formal_durable_evidence")
    if repair:
        phase = "depth_repair"
    elif retention:
        phase = "retention_readiness"
    elif coverage:
        phase = "depth_repair"
        reasons.append("depth_confirmation_after_coverage")
    else:
        phase = "coverage"
    return {
        "version": VERSION, "phase": phase,
        "coverage_checkpoint_reached": coverage,
        "repair_priority": repair, "retention_priority": retention,
        "reason_codes": reasons, "missing_evidence": missing,
        "provisional": True, "selection_authority": False,
        "evidence": {
            "field_checkpoints": checkpoints,
            "current_repairing_nodes": counts["repairing"],
            "critical_safety_unresolved_count": safety,
            "recheck_due_nodes": due, "scheduled_retention_nodes": scheduled,
            "durable_nodes": durable,
        },
    }
