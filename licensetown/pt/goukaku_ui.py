import os
from urllib.parse import parse_qs

from flask import Blueprint, abort, redirect, render_template, request, url_for
from itsdangerous import BadSignature, URLSafeSerializer, URLSafeTimedSerializer

from database import (
    calculate_overall_progress,
    database_is_available,
    get_dashboard_learning_data,
    get_db_connection,
    get_field_learning_summary,
    get_learning_activity,
    get_learning_events,
    get_question_attempts,
    record_activity_event,
    get_weekly_question_history,
    get_supported_learner_ids,
    user_names,
)
from dashboard_read_bundle import get_dashboard_read_bundle as _get_production_dashboard_read_bundle
from dashboard_read_bundle import get_learner_navigation_read_bundle as _get_production_learner_navigation_read_bundle
from trial100_store import get_trial100_records
from learning_analysis import build_gensan_comment, build_learning_guidance
from supporter_report import build_supporter_report
from supporter_performance import measure
from pilot_diagnostics import build_pilot_diagnostics
from field_evidence import build_field_evidence
from field_progress import build_field_progress
from dashboard_real_data_shadow import build_dashboard_real_data_shadow
from adaptive_question_selector import parse_node_adaptive_pilot_user_ids
from pass_readiness import build_pass_readiness
from learner_readiness_presentation import build_learner_readiness_presentation
from field_progress_presentation import build_field_progress_presentation_from_calculation
from overall_progress_presentation import build_overall_progress_presentation
from dashboard_settings import (
    get_daily_question_goal,
    get_effective_exam_date,
    get_reward_progress,
    tokyo_today,
)
from learning_milestones import build_learning_milestones
from judgment_shadow import build_shadow_judgment
from phase12_presentation import build_phase12_presentation
import learner_path_performance as learner_path_perf


goukaku_ui = Blueprint("goukaku_ui", __name__)

# Parent/supporter links are long-lived product links. Keep a bounded credential
# lifetime, while active supporter_links remains the revocation authority.
SUPPORTER_TOKEN_MAX_AGE_SECONDS = 365 * 24 * 60 * 60


def field_progress_ui_enabled():
    return os.getenv("ENABLE_FIELD_PROGRESS_UI", "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def overall_progress_ui_enabled():
    return os.getenv("ENABLE_OVERALL_PROGRESS_UI", "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def dashboard_real_data_shadow_enabled():
    return os.getenv("ENABLE_DASHBOARD_REAL_DATA_SHADOW", "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def phase12_guidance_preview_enabled():
    return os.getenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def learning_strategy_v1_enabled_for_user(user_id):
    """Use the same Stage E pilot gate as adaptive_daily runtime selection."""
    enabled = os.getenv("ENABLE_LEARNING_STRATEGY_V1", "false").strip().lower() in {
        "1", "true", "yes", "on",
    }
    pilot_ids = parse_node_adaptive_pilot_user_ids(
        os.getenv("LEARNING_STRATEGY_PILOT_USER_IDS")
    )
    return bool(enabled and user_id and user_id in pilot_ids)


def create_dashboard_token(user_id):
    serializer = URLSafeSerializer(
        os.getenv("CHANNEL_SECRET", "local-dashboard-secret"),
        salt="goukaku-dashboard",
    )
    return serializer.dumps({"user_id": user_id})


def dashboard_user_id(token):
    if not token:
        return None
    serializer = URLSafeSerializer(
        os.getenv("CHANNEL_SECRET", "local-dashboard-secret"),
        salt="goukaku-dashboard",
    )
    try:
        return serializer.loads(token).get("user_id")
    except (BadSignature, AttributeError):
        return None


def authorized_dashboard_learner(token):
    """Resolve a signed learner dashboard token or fail closed."""
    user_id = dashboard_user_id(token)
    if not user_id:
        abort(403)
    return user_id


def learner_dashboard_token(args):
    """Resolve the signed token carrier used by direct and LIFF dashboard entry."""
    if "token" in args:
        return args.get("token")

    liff_state = args.get("liff.state")
    if not isinstance(liff_state, str) or not liff_state.startswith("?"):
        return None
    try:
        state_params = parse_qs(
            liff_state[1:],
            keep_blank_values=True,
            strict_parsing=True,
        )
    except ValueError:
        return None
    tokens = state_params.get("token", [])
    if len(tokens) != 1 or not tokens[0]:
        return None
    return tokens[0]


def create_supporter_token(supporter_user_id):
    serializer = URLSafeTimedSerializer(
        os.getenv("CHANNEL_SECRET", "local-dashboard-secret"),
        salt="supporter-dashboard",
    )
    return serializer.dumps({"supporter_user_id": supporter_user_id})


def supporter_user_id(token):
    if not token:
        return None
    serializer = URLSafeTimedSerializer(
        os.getenv("CHANNEL_SECRET", "local-dashboard-secret"),
        salt="supporter-dashboard",
    )
    try:
        return serializer.loads(
            token,
            max_age=SUPPORTER_TOKEN_MAX_AGE_SECONDS,
        ).get("supporter_user_id")
    except (BadSignature, AttributeError):
        return None


def authorized_supporter_learner(token, requested_learner_id=None):
    """署名済みsupporterとactiveなリンクの両方から閲覧対象を確定する。"""
    supporter_id = supporter_user_id(token)
    if not supporter_id:
        abort(403)
    learner_ids = get_supported_learner_ids(supporter_id)
    if not learner_ids:
        abort(403)
    if requested_learner_id:
        if requested_learner_id not in learner_ids:
            abort(403)
        return supporter_id, requested_learner_id
    return supporter_id, learner_ids[0]


def _authorized_supporter_learner_with_connection(
    token,
    requested_learner_id,
    connection,
):
    """Production /supporter用。既存認可意味を保ったままcaller connectionを使う。"""
    supporter_id = supporter_user_id(token)
    if not supporter_id:
        abort(403)
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT learner_user_id FROM supporter_links
            WHERE supporter_user_id = %s AND is_active = TRUE
            ORDER BY created_at, id
            """,
            (supporter_id,),
        )
        learner_ids = [row[0] for row in cur.fetchall()]
    if not learner_ids:
        abort(403)
    if requested_learner_id:
        if requested_learner_id not in learner_ids:
            abort(403)
        return supporter_id, requested_learner_id
    return supporter_id, learner_ids[0]


def _user_name_with_connection(user_id, connection, default="学習者"):
    """Production /supporterでプロフィール名を同じDB connectionから読む。"""
    with connection.cursor() as cur:
        cur.execute("SELECT name FROM user_profiles WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
    if row is None or row[0] is None:
        return default
    return row[0]


def _dashboard_read_bundle(
    user_id, *, include_attempts=False, include_trial100=False, include_learning_events=False
):
    """Use the shared Production read path while preserving local/test hooks."""
    if database_is_available():
        bundle = _get_production_dashboard_read_bundle(
            user_id,
            include_attempts=include_attempts,
            include_trial100=include_trial100,
            include_learning_events=include_learning_events,
        )
    else:
        bundle = {
            "learning_data": get_dashboard_learning_data(user_id),
            "attempts": get_question_attempts(user_id) if include_attempts else [],
            "trial100_records": get_trial100_records(user_id) if include_trial100 else [],
            "learning_events": get_learning_events(user_id) if include_learning_events else [],
        }

    if include_attempts:
        from licensetown.pt.formal_attempt_evidence import filter_current_formal_evidence
        bundle = dict(bundle)
        bundle["attempts"] = filter_current_formal_evidence(bundle.get("attempts") or [])
    return bundle


def get_learner_navigation_formal_inputs(user_id):
    """Read only the current formal evidence needed to reproduce today's CTA."""
    if database_is_available():
        bundle = _get_production_learner_navigation_read_bundle(user_id)
    else:
        bundle = {
            "attempts": get_question_attempts(user_id),
            "trial100_records": get_trial100_records(user_id),
            "learning_events": get_learning_events(user_id),
        }

    from licensetown.pt.formal_attempt_evidence import filter_current_formal_evidence
    bundle = dict(bundle)
    bundle["attempts"] = filter_current_formal_evidence(bundle.get("attempts") or [])
    return bundle


def _subjects_learning_data(user_id):
    """Return raw activity plus current-formal field performance for subject pages."""
    if database_is_available():
        learning_data = _get_production_dashboard_read_bundle(user_id)["learning_data"]
        return learning_data["fields"], learning_data["activity"]
    return get_field_learning_summary(user_id), get_learning_activity(user_id)


def _stage_e_shadow_authority(shadow_result, strategy):
    """Project Stage E's ranked field decision into the learner-navigation contract."""
    ranked = [
        row for row in (strategy.get("ranked_fields") or [])
        if row.get("allocation_candidate") and float(row.get("priority_score") or 0) > 0
    ][:3]
    if not ranked:
        return shadow_result

    field_facts = {
        int(row["field_id"]): row for row in shadow_result.get("fields", [])
    }

    def adapt(row):
        intent = str(row.get("learning_intent") or "coverage")
        safety = float((row.get("priority_components") or {}).get("safety_score") or 0) > 0
        if safety or intent == "safety_review":
            reason_code = "safety_repair"
            selector_intent = "repair"
        elif intent == "coverage":
            reason_code = "coverage_expand"
            selector_intent = "exploration"
        elif intent in {"retention", "maintenance"}:
            reason_code = "retention_recheck"
            selector_intent = "recheck"
        elif intent == "strategy_change":
            reason_code = "strategy_change"
            selector_intent = "strategy_change"
        else:
            reason_code = "low_progress_repair"
            selector_intent = "repair"
        field_id = int(row["field_id"])
        facts = field_facts.get(field_id, {})
        evaluation = (row.get("target") or {}).get("evaluation") or {}
        proven = bool(
            safety
            or (
                evaluation.get("evidence_sufficient")
                and row.get("field_state") == "weak"
            )
        )
        return {
            "field_id": field_id,
            "field_name": row.get("field_name"),
            "reason_code": reason_code,
            "learning_intent": selector_intent,
            "is_proven_weakness": proven,
            "is_coverage_priority": reason_code == "coverage_expand",
            "field_progress_score": facts.get("field_progress_score"),
            "field_progress_percent": facts.get("field_progress_percent"),
            "node_coverage": facts.get("node_coverage"),
            "evaluable_answer_count": facts.get("evaluable_answer_count"),
        }

    priority = [adapt(row) for row in ranked]
    primary = priority[0]
    result = dict(shadow_result)
    result["priority_top3"] = priority
    result["recommendation_intent"] = {
        "target_field_id": primary["field_id"],
        "target_field": primary["field_name"],
        "target_canonical_node_ids": [],
        "learning_intent": primary["learning_intent"],
        "priority_reason": primary["reason_code"],
        "safety_priority": primary["reason_code"] == "safety_repair",
        "new_vs_review_preference": (
            "new" if primary["reason_code"] == "coverage_expand" else "review"
        ),
        "requested_question_count": 10,
        "exact_question_ids": None,
        "selector_owns_exact_q": True,
    }
    result["strategy_authority"] = {
        "version": strategy.get("version"),
        "recommended_field_id": strategy.get("recommended_field_id"),
        "recommended_field_name": strategy.get("recommended_field_name"),
    }
    return result


def build_learner_navigation_from_formal_inputs(
    attempts,
    trial100_records,
    *,
    learning_events=None,
    use_stage_e_strategy=False,
    days_to_exam=None,
    evidence=None,
    progress=None,
    shadow_result=None,
):
    """Build the same structured learner CTA without legacy dashboard work."""
    attempts = list(attempts or [])
    from learning_strategy_runtime_pilot import trusted_strategy_evidence_attempts
    trusted_attempts, _excluded_provisional = trusted_strategy_evidence_attempts(attempts)
    evidence = evidence or build_field_evidence(trusted_attempts)
    progress = progress or build_field_progress(evidence)
    shadow_result = shadow_result or build_dashboard_real_data_shadow(
        trusted_attempts,
        evidence=evidence,
        progress=progress,
    )
    if use_stage_e_strategy:
        try:
            from datetime import datetime, timezone
            from learning_strategy_runtime_pilot import strategy_snapshot
            stage_e = strategy_snapshot(
                trusted_attempts,
                list(learning_events or []),
                datetime.now(timezone.utc),
                days_to_exam=days_to_exam,
            )
            shadow_result = _stage_e_shadow_authority(shadow_result, stage_e)
        except (KeyError, TypeError, ValueError):
            # Fail closed to the existing formal dashboard evidence when the
            # Stage E completion context is not yet reproducible.
            pass
    readiness = build_pass_readiness(
        trusted_attempts,
        field_evidence=evidence,
        progress=progress,
        trial100_records=trial100_records,
    )
    return build_learner_readiness_presentation(readiness, shadow_result)


def _phase12_shadow_from_navigation(navigation):
    """Mirror the single learner-navigation decision into the current-position card."""
    action = dict((navigation or {}).get("today_action") or {})
    field = action.get("field")
    count = int(action.get("count") or 0)
    if not field or count <= 0:
        return None
    return {
        "learning_intent": str(action.get("learning_intent") or "exploration"),
        "target_field": field,
        "question_count": count,
        "recommended_route": "dashboard_recommendation",
        "reason_code": str(action.get("reason_code") or "coverage_expand"),
    }


def build_dashboard(user_id=None, include_learner_navigation=False):
    today = tokyo_today()
    exam_date = get_effective_exam_date(user_id)
    dashboard = {
        "current_date": today,
        "exam_date": exam_date,
        "days_until_exam": max((exam_date - today).days, 0) if exam_date else None,
        "exam_is_tentative": True,
        "overall_progress": 0,
        "total_answers": 0,
        "unique_answered_questions": 0,
        "correct_answers": 0,
        "study_minutes": 0,
        "last_7_days_accuracy": 0,
        "average_accuracy": 0,
        "field_stats": [],
        "field_progress_ui_enabled": False,
        "field_progress_fields": [],
        "overall_progress_ui_enabled": False,
        "overall_progress_preview": None,
        "dashboard_real_data_shadow_enabled": False,
        "dashboard_real_data_shadow": None,
        "learner_navigation_enabled": False,
        "learner_navigation": None,
        "phase12_guidance_preview_enabled": False,
        "phase12_guidance_preview": None,
        "weak_fields": [],
        "weak_analysis_message": "まずは100問を目標に基礎を固めましょう。",
        "recommended_study": [],
        "recommendation_reason": None,
        "recommendation_progress": 0,
        "recommendation_goal": 0,
        "today_goal": get_daily_question_goal(user_id),
        "today_progress": 0,
        "streak_days": 0,
        **get_reward_progress(0),
        "gensan_comment": "今日はまだ来てねぇな。5問だけやるか？＾＾",
    }
    if user_id:
        field_preview = field_progress_ui_enabled()
        overall_preview = overall_progress_ui_enabled()
        shadow_preview = dashboard_real_data_shadow_enabled()
        phase12_preview = phase12_guidance_preview_enabled()
        strategy_navigation = bool(
            include_learner_navigation and learning_strategy_v1_enabled_for_user(user_id)
        )
        needs_attempts = bool(
            field_preview
            or overall_preview
            or shadow_preview
            or phase12_preview
            or include_learner_navigation
        )
        bundle = _dashboard_read_bundle(
            user_id,
            include_attempts=needs_attempts,
            include_trial100=include_learner_navigation,
            include_learning_events=strategy_navigation,
        )
        learning_data = bundle["learning_data"]
        dashboard.update(learning_data["summary"])
        dashboard.update(learning_data["activity"])
        dashboard["unique_answered_questions"] = learning_data["unique_question_count"]
        dashboard["overall_progress"] = calculate_overall_progress(
            dashboard["study_minutes"],
            dashboard["total_answers"],
            dashboard["unique_answered_questions"],
        )
        fields = learning_data["fields"]
        dashboard["field_stats"] = [item for item in fields if item["learned"]]
        attempts = bundle["attempts"] if needs_attempts else None
        evidence = None
        progress = None
        if needs_attempts:
            evidence = build_field_evidence(attempts)
        if field_preview or overall_preview or shadow_preview or include_learner_navigation:
            progress = build_field_progress(evidence)
        if field_preview or include_learner_navigation:
            dashboard["field_progress_ui_enabled"] = True
            dashboard["field_progress_fields"] = build_field_progress_presentation_from_calculation(
                evidence, progress, legacy_fields=fields
            )
        if overall_preview or include_learner_navigation:
            dashboard["overall_progress_ui_enabled"] = True
            dashboard["overall_progress_preview"] = build_overall_progress_presentation(
                progress, overall_accuracy_percent=dashboard["average_accuracy"]
            )
        current_guidance = build_learning_guidance(dashboard["total_answers"], fields)
        dashboard.update(current_guidance)
        shadow_result = None
        if shadow_preview or include_learner_navigation:
            legacy_recommended_field = (
                dashboard["recommended_study"][0][0]
                if dashboard["recommended_study"] else None
            )
            shadow_result = build_dashboard_real_data_shadow(
                attempts,
                evidence=evidence,
                progress=progress,
                legacy_overall_progress_percent=dashboard["overall_progress"],
                legacy_weak_fields=dashboard["weak_fields"],
                legacy_recommended_field=legacy_recommended_field,
            )
            if shadow_preview:
                dashboard["dashboard_real_data_shadow_enabled"] = True
                dashboard["dashboard_real_data_shadow"] = shadow_result
        if include_learner_navigation:
            dashboard["learner_navigation_enabled"] = True
            dashboard["learner_navigation"] = build_learner_navigation_from_formal_inputs(
                attempts,
                bundle["trial100_records"],
                learning_events=bundle.get("learning_events"),
                use_stage_e_strategy=strategy_navigation,
                days_to_exam=dashboard["days_until_exam"],
                evidence=evidence,
                progress=progress,
                shadow_result=shadow_result,
            )
        if phase12_preview:
            shadow_judgment = None
            if dashboard["learner_navigation_enabled"]:
                shadow_judgment = _phase12_shadow_from_navigation(
                    dashboard["learner_navigation"]
                )
            if shadow_judgment is None:
                shadow_judgment = build_shadow_judgment(
                    attempts,
                    evidence,
                    current_guidance,
                )
            dashboard["phase12_guidance_preview_enabled"] = True
            dashboard["phase12_guidance_preview"] = build_phase12_presentation(
                shadow_judgment,
                evidence,
            )
        if dashboard["recommended_study"]:
            recommended_name, recommended_count = dashboard["recommended_study"][0]
            recommended_field = next(
                (field for field in fields if field["name"] == recommended_name),
                None,
            )
            today_answered_count = (
                recommended_field.get("today_answered_count", 0)
                if recommended_field
                else 0
            )
            dashboard["recommendation_goal"] = recommended_count
            dashboard["recommendation_progress"] = min(
                today_answered_count,
                recommended_count,
            )
        dashboard.update(get_reward_progress(dashboard["total_answers"]))
        gensan_recommended_study = dashboard["recommended_study"]
        if dashboard["learner_navigation_enabled"]:
            formal_action = (dashboard["learner_navigation"] or {}).get("today_action") or {}
            if formal_action.get("field"):
                gensan_recommended_study = [(
                    formal_action["field"],
                    int(formal_action.get("count") or 5),
                )]
        dashboard["gensan_comment"] = build_gensan_comment(
            dashboard["total_answers"],
            fields,
            dashboard["weak_fields"],
            gensan_recommended_study,
            dashboard["streak_days"],
            dashboard["today_progress"],
        )
    return dashboard


@goukaku_ui.route("/goukaku-no-michi")
@learner_path_perf.timed("dashboard.route_total")
def home():
    token = learner_dashboard_token(request.args)
    user_id = authorized_dashboard_learner(token)
    with learner_path_perf.measure("dashboard.build"):
        dashboard = build_dashboard(user_id, include_learner_navigation=True)
    navigation = dashboard.get("learner_navigation") or {}
    action = navigation.get("today_action") or {}
    if action.get("field"):
        with learner_path_perf.measure("dashboard.activity_record"):
            record_activity_event(
                user_id,
                "recommendation_plan",
                {
                    "field": action["field"],
                    "goal": action["count"],
                    "learning_intent": action["learning_intent"],
                    "reason_code": action["reason_code"],
                    "source": "learner_navigation",
                },
            )
    elif dashboard["recommended_study"]:
        recommended_name, recommended_count = dashboard["recommended_study"][0]
        with learner_path_perf.measure("dashboard.activity_record"):
            record_activity_event(
                user_id,
                "recommendation_plan",
                {"field": recommended_name, "goal": recommended_count},
            )
    with learner_path_perf.measure("dashboard.template_render"):
        return render_template(
            "goukaku/home.html",
            dashboard=dashboard,
            dashboard_token=token,
            dashboard_title="合格への道",
            read_only=False,
            learner_preview=False,
            subjects_url=url_for("goukaku_ui.subjects", token=token),
            line_official_account_id=os.getenv("LINE_OFFICIAL_ACCOUNT_ID", "").strip(),
            liff_id=os.getenv("LIFF_ID", "").strip(),
        )


@goukaku_ui.route("/goukaku-no-michi/subjects")
def subjects():
    token = request.args.get("token")
    user_id = authorized_dashboard_learner(token)
    subjects, activity = _subjects_learning_data(user_id)
    recent_fields = [item for item in subjects if item["recent_7d_answered_count"]]
    top_recent_field = max(
        recent_fields, key=lambda item: item["recent_7d_answered_count"], default=None
    )
    return render_template(
        "goukaku/subjects.html",
        subjects=subjects,
        activity=activity,
        top_recent_field=top_recent_field,
        dashboard_token=token,
        read_only=False,
        return_url=url_for("goukaku_ui.home", token=token),
    )


@goukaku_ui.route("/goukaku-no-michi/footprints")
def footprints():
    token = request.args.get("token")
    user_id = authorized_dashboard_learner(token)
    events = build_learning_milestones(get_question_attempts(user_id), limit=5)
    return render_template(
        "goukaku/footprints.html",
        events=events,
        return_url=url_for("goukaku_ui.home", token=token),
    )


@goukaku_ui.route("/goukaku-no-michi/learning")
def learning():
    token = request.args.get("token")
    authorized_dashboard_learner(token)
    return redirect(url_for("goukaku_ui.home", token=token))


@goukaku_ui.route("/supporter")
def supporter_dashboard():
    token = request.args.get("token")
    requested_learner_id = request.args.get("learner_user_id")
    if database_is_available():
        with get_db_connection() as conn:
            with measure("supporter.authorization"):
                _, learner_id = _authorized_supporter_learner_with_connection(
                    token,
                    requested_learner_id,
                    conn,
                )
            report = build_supporter_report(learner_id, _connection=conn)
            with measure("supporter.learner_name"):
                learner_name = _user_name_with_connection(learner_id, conn)
    else:
        with measure("supporter.authorization"):
            _, learner_id = authorized_supporter_learner(
                token,
                requested_learner_id,
            )
        report = build_supporter_report(learner_id)
        with measure("supporter.learner_name"):
            learner_name = user_names.get(learner_id, "学習者") or "学習者"
    with measure("supporter.template_render"):
        response = render_template(
            "goukaku/supporter.html",
            learner_name=learner_name,
            learner_id=learner_id,
            supporter_token=token,
            report=report,
        )
    return response


@goukaku_ui.route("/supporter/weekly-question-history")
def supporter_weekly_question_history():
    token = request.args.get("token")
    _, learner_id = authorized_supporter_learner(token, request.args.get("learner_user_id"))
    learner_name = user_names.get(learner_id, "学習者") or "学習者"
    return render_template("goukaku/supporter_weekly_questions.html", learner_name=learner_name,
                           learner_id=learner_id, supporter_token=token,
                           weekly=get_weekly_question_history(learner_id))


@goukaku_ui.route("/supporter/pilot-diagnostics")
def supporter_pilot_diagnostics():
    token = request.args.get("token")
    _, learner_id = authorized_supporter_learner(token, request.args.get("learner_user_id"))
    period = request.args.get("period", "7")
    if period not in {"7", "30", "all"}:
        period = "7"
    return render_template("goukaku/supporter_pilot_diagnostics.html",
                           diagnostics=build_pilot_diagnostics(learner_id, period),
                           learner_id=learner_id, supporter_token=token)


@goukaku_ui.route("/supporter/goukaku-no-michi")
def supporter_goukaku_home():
    token = request.args.get("token")
    _, learner_id = authorized_supporter_learner(
        token,
        request.args.get("learner_user_id"),
    )
    learner_name = user_names.get(learner_id, "学習者") or "学習者"
    return render_template(
        "goukaku/home.html",
        dashboard=build_dashboard(learner_id),
        dashboard_token=None,
        dashboard_title=f"{learner_name}さんの合格への道",
        learner_name=learner_name,
        read_only=True,
        learner_preview=False,
        subjects_url=url_for(
            "goukaku_ui.supporter_goukaku_subjects",
            token=token,
            learner_user_id=learner_id,
        ),
        supporter_return_url=url_for(
            "goukaku_ui.supporter_dashboard",
            token=token,
            learner_user_id=learner_id,
        ),
        line_official_account_id="",
        liff_id="",
    )


@goukaku_ui.route("/supporter/goukaku-no-michi/learner-preview")
def supporter_learner_preview():
    token = request.args.get("token")
    _, learner_id = authorized_supporter_learner(
        token,
        request.args.get("learner_user_id"),
    )
    return render_template(
        "goukaku/home.html",
        dashboard=build_dashboard(learner_id),
        dashboard_token=None,
        dashboard_title="合格への道",
        read_only=False,
        learner_preview=True,
        subjects_url=None,
        supporter_return_url=None,
        line_official_account_id="",
        liff_id="",
    )


@goukaku_ui.route("/supporter/goukaku-no-michi/subjects")
def supporter_goukaku_subjects():
    token = request.args.get("token")
    _, learner_id = authorized_supporter_learner(
        token,
        request.args.get("learner_user_id"),
    )
    subjects, activity = _subjects_learning_data(learner_id)
    recent_fields = [item for item in subjects if item["recent_7d_answered_count"]]
    top_recent_field = max(
        recent_fields, key=lambda item: item["recent_7d_answered_count"], default=None
    )
    return render_template(
        "goukaku/subjects.html",
        subjects=subjects,
        activity=activity,
        top_recent_field=top_recent_field,
        dashboard_token=None,
        read_only=True,
        return_url=url_for(
            "goukaku_ui.supporter_goukaku_home",
            token=token,
            learner_user_id=learner_id,
        ),
    )
