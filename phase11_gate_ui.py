"""Internal-only Phase11 gate dashboard.

This view exposes already-computed diagnostic evidence without changing learner
recommendations, selector behavior, Node state, or Production data.
"""

from __future__ import annotations

from flask import abort, render_template, request

from database import get_learning_events, get_question_attempts
from developer_ui import require_developer_authorization
from knowledge_node_state_transition import derive_all_user_node_states
from phase11_promotion_gate_status import build_phase11_promotion_gate_status
from phase11_repair_effectiveness_facts import build_same_day_repair_effectiveness_facts
from phase11_retention_horizon_facts import build_retention_horizon_facts
from phase11_retention_outcome_audit import build_retention_outcome_audit
from phase11_retention_supply_audit import build_retention_supply_audit
from phase11_session_load_facts import build_same_day_session_load_facts
from pilot_diagnostics import build_pilot_diagnostics


ROUTE = "/internal/phase11-gates"
ENDPOINT = "internal_phase11_gates"


def build_phase11_gate_dashboard(learner_id: str, period: str = "7") -> dict:
    """Build one read-only snapshot from formal history and existing diagnostics."""
    if period not in {"7", "30", "all"}:
        period = "7"

    diagnostics = build_pilot_diagnostics(learner_id, period)
    attempts = get_question_attempts(learner_id)
    node_states = derive_all_user_node_states(attempts)
    retention_horizon = build_retention_horizon_facts(node_states)
    retention_outcomes = build_retention_outcome_audit(attempts)
    retention_supply = build_retention_supply_audit(node_states)
    gate_status = build_phase11_promotion_gate_status(
        retrospective_shadow_audit=diagnostics.get("retrospective_shadow_audit"),
        repeat_structure_audit=diagnostics.get("repeat_structure_audit"),
        retention_horizon=retention_horizon,
        retention_outcome_audit=retention_outcomes,
        state_counts=diagnostics.get("state_counts"),
        transitions={
            "recheck_due_to_stable": diagnostics.get("due_to_stable", 0),
            "recheck_due_to_repairing": diagnostics.get("due_to_repairing", 0),
        },
        shadow_judgment=diagnostics.get("shadow_judgment"),
    )
    return {
        "period": period,
        "diagnostics": diagnostics,
        "session_load": build_same_day_session_load_facts(attempts),
        "repair_effectiveness": build_same_day_repair_effectiveness_facts(
            get_learning_events(learner_id)
        ),
        "retention_horizon": retention_horizon,
        "retention_outcomes": retention_outcomes,
        "retention_supply": retention_supply,
        "gate_status": gate_status,
    }


def install_phase11_gate_ui(flask_app) -> None:
    """Register the internal dashboard exactly once."""
    if ENDPOINT in flask_app.view_functions:
        return

    def internal_phase11_gates():
        token = require_developer_authorization()
        learner_id = request.args.get("learner_user_id", "").strip()
        if not learner_id:
            abort(400)
        period = request.args.get("period", "7")
        snapshot = build_phase11_gate_dashboard(learner_id, period)
        return render_template(
            "internal/phase11_gates.html",
            internal_token=token,
            learner_id=learner_id,
            **snapshot,
        )

    flask_app.add_url_rule(ROUTE, ENDPOINT, internal_phase11_gates, methods=["GET"])
