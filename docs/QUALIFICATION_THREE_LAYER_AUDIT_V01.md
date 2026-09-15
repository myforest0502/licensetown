# Qualification three-layer audit v0.1

Date: 2026-09-15. Baseline: `30a208a60ca34e23e72e279249713c758e4c0695` (fetched main).

## Decision and evidence boundary

This is an ownership and dependency audit, with corrections to stale module
descriptions. **No file is moved and no executable statement is changed.**
Existing locations are compatibility boundaries, not claims of shared semantics.
The inventory covers tracked root Python modules, the complete qualifications
package, and repository directory families. Imports were inspected statically;
this is not a live database/schema inspection or production acceptance audit.

PT truth remains attempts -> derived Node state -> field/strategy/readiness ->
selector/presentation. Stage E supplies field/intent candidates to the opt-in PT
pilot; adaptive selector owns exact Q IDs. Phase11 remains HOLD / Shadow-only.
No production flag is read or changed by this work.

## Current structure and classification

```text
qualifications/
  __init__.py                   metadata lookup, PT default identity
  base.py, bank_provider.py,
  provider_registry.py          legacy re-export interfaces
  common/
    base.py                    A: QualificationConfig
    bank_provider.py           A: QuestionBankProvider protocol
    learning_store.py          A: LearningHistoryStore protocol
    provider_registry.py       D: composition exception (concrete PT imports)
    learning_store_registry.py D: composition exception (PT + database imports)
  pt/
    config.py                  B: PT identity
    provider.py                B: existing root bank adapter
    learning_store.py          B: PT-qualified reads/state/reset
    learning_writer.py         B: PT-qualified writes
  takken/
    config.py                  E: identity only
    __init__.py                E: dormant package
```

`common/__init__.py` is a minimal package marker. PT/Takken config use the shared
metadata class. Legacy re-exports retain object identity. The registry *lookup
contract* is shared, but its current registration wiring is not dependency-pure
common. Do not report all files inside common as already fully separated (A).

PT provider is used by `learning_engine.py` and `adaptive_question_selector.py`;
its old “not connected to runtime” description was stale. `qualifications` remains
metadata-only at package import, but its submodules are used in PT runtime.

## Repository families

| Location | Ownership / present role | Decision |
|---|---|---|
| Root Python modules | PT policy plus application composition and service infrastructure; complete inventory below | Retain current imports |
| `data/question_bank/` | C: formal PT Q1-Q2000, tags, KN master/aliases, equivalence and strong repair pairs | Fixed runtime paths; do not move |
| Other `data/`, `questions_master.json` | Existing supporting/legacy inputs; app explicitly reads root questions_master | Do not infer unused or delete |
| `templates/`, `static/` | D: Flask UI foundation mixed with PT learner language | Keep paths and template/asset names |
| `preview-pc/`, `preview-724/`, `preview-responsive/` | D: site assets exposed by site_ui routes | Names do not mean obsolete; keep |
| `marketing/` | Presentation/source materials, not proof of domain-neutral UI | Keep; review publication references before any later move |
| `scripts/` | Mixed validation, audit, maintenance and integration tools; Stage F audits are PT | Never run maintenance as part of cleanup |
| `reports/` | PT bank build/audit history and strategy evidence; includes Python tools | Preserve provenance, script imports and report paths |
| `staging/` | PT bank historical preparation inputs, not a Takken bank | Preserve; no integration/build operations |
| `migrations/` | Historical persistence deployment changes | No execution or schema edits |
| `docs/` | Product/state contracts plus PT-specific and architecture documents | Keep links stable; add this index |
| `tests/` | Shared boundary checks and extensive PT/data/path fixtures | Keep; run full suite with isolated environment |
| `.github/`, `Procfile`, `requirements.txt`, `.gitignore` | Service/build/CI infrastructure | No changes; some historical workflows write data on specific branches |
| `AGENTS.md`, `README.md` | Development/product entry points | Keep |

## Dependency direction and import risk

Desired dependency is concrete PT/Takken -> common contracts. Current wiring:

```text
qualifications -> common.base + pt.config + takken.config
legacy qualification shims -> common contracts/registry
common.provider_registry -> pt.provider -> root question_bank
common.learning_store_registry -> pt.learning_store -> root database
pt.learning_writer -> root database -> root question_bank
question_bank -> question_equivalence -> knowledge_node_canonical
wsgi -> app + qualification_*_scope installers + session/UI installers
learning_engine / adaptive_question_selector -> pt.provider + root PT helpers
```

Registry wiring is an explicit retained exception, not a newly introduced
inversion. Moving registration out now would require coordinating import order,
singleton ownership and compatibility call sites. Do not make database or bank
loaders import those registries in return: that would risk a partially initialized
module cycle. Do not eagerly export store/provider from package `__init__`.
Store imports can reach database initialization; contract-only imports must not.

The tracked `Procfile` says `gunicorn --timeout 90 app:app`, whereas `wsgi.py`
contains the production composition installers. Do not assume those entry points
are interchangeable or that Procfile proves the live Render start command. Live
Render configuration is outside this audit; both paths remain untouched.

`wsgi.py` installs PT-qualified history/writer/dashboard/time composition over
legacy modules. Its installation order and captured functions matter. This is
why replacing root modules with apparent aliases needs dedicated import-order
and monkeypatch compatibility evidence, not just matching return values.

## Safe candidates versus retained locations

| Candidate | Main consumers / risk | Difficulty and prerequisite |
|---|---|---|
| Stale package/provider/registry/Stage E descriptions | Developers previously told adapter/Stage E were disconnected | LOW: corrected here; executable AST equivalence checked |
| `exam_weight_shadow.py` | Stage D, tests; explicit 18-field counts and PT provenance | MEDIUM: future PT home possible, but retain constants/function globals and legacy imports; no current behavior reason to move |
| `field_evaluation_shadow.py`, `field_progress.py` | Stage D, dashboard/readiness; pure arithmetic still consumes PT evidence/state contract | MEDIUM: prove domain contract with actual second qualification before common extraction |
| Stage C/D/E/F and Phase11 helpers | PT field/KN/Safety/concentration policies and audit imports | HIGH: keep PT ownership even where functions look generic |
| `question_bank.py`, canonical/equivalence/repair modules | database, selector, state transition, scripts and tests | HIGH: `Path(__file__).parent/data/question_bank` and import-time loading; would need explicit data-root boundary first |
| `database.py`, qualification scope hooks, durable sessions | WSGI, UI, LINE, PT store/writer; initialization and replacement order | HIGH: preserve call interfaces, legacy fallback and qualified SQL; not a cleanup migration |
| `app.py`, `wsgi.py`, `Procfile`, requirements and UI directories | Gunicorn startup, Flask routes/assets, tests | HIGH: no first move; deployment and path contracts remain |
| Generic email/payment/timing helpers | App-wide service behavior and configuration references | MEDIUM: possible shared services later; not automatically a qualification/common responsibility |

No physical move was selected. This is deliberate completion of the safe scope,
not an unfinished relocation. A re-export alone does not preserve assignment to
module constants, function globals, import side effects, or module identity.
No new facade is added just to make the directory tree look different.

## PT and persistence boundaries that must remain visible

- PT data is closed `2026-09-b20`, 2000 records (900 original / 1100 past exam).
  Q IDs are stable inside PT, not universal qualification identities.
- KNOW/MEASURE/INTERPRET/PREDICT/PRESCRIBE/DECIDE, critical/moderate Safety,
  18-field membership, KN repair/equivalence and exam weights are PT semantics.
- `dashboard_settings.py` defaults to 2027-02-21; this is PT configuration mixed
  with generally useful time helpers, not a shared exam date.
- Existing PT store/writer and scope hooks already qualify production SQL.
  `qualification_user_state` handles initial assessment; legacy profile state and
  no-DATABASE_URL fallbacks remain PT compatibility paths. This audit does not
  repeat the old claim that qualification_id is absent everywhere.
- Provider abstraction is intentionally small. Remaining root bank helpers and
  category_small usage mean the learning engine/selector is not a generic engine.
- `site_ui.py` serves preview directories by fixed names; `app.py` retains the
  root `questions_master.json` read path. Neither is safe to remove by naming.

## Takken boundary and next blocker

Only identity is configured. Both registries recognize takken but raise their
NotConfigured exception; unknown IDs raise KeyError. PT fallback is forbidden.
Existing tests already cover provider/store fail-closed behavior and qualified
PT reads/writes/sessions. No duplicate registration framework or sample bank is
needed for this task.

The next real Takken slice requires authoritative stable question IDs, question
records, answer/grading and explanation data, source/provenance rights, reviewed
field taxonomy/tags, KN identity, equivalence and repair evidence definitions,
and exam-specific strategy/Safety/weight rules where applicable. Their meaning
must not be copied from PT. Only then can shared retrieval, taxonomy and state
interfaces be judged against two real qualifications. See
`TAKKEN_PHASE_E_READINESS_V01.md` for the staged readiness boundary.

## Validation and production impact

Validation results are recorded in CURRENT_STATE with this change. Focused checks
cover provider identity/parity, package import isolation, registry fail-closed,
qualified history/writer/dashboard/time/session/reset, strategy pilot gates and
repeat/selector regressions. Full pytest uses DATABASE_URL empty and dummy API
credentials; the existing external-fixture deselection matches CI. Formal bank
validator is run separately. Local tests are evidence of regression coverage,
not a new real-learner acceptance or promotion decision.

No DB access to production, migration, Render operation, environment setting,
LINE UX change, bank data edit, Stage E authority change or Phase11 promotion.
Only docs and module docstrings are edited. Main is not merged or deployed here.

## Complete root Python ownership inventory

The following static inventory includes local import dependencies (including
function-local imports). C means PT-owned even when retained at root; D means
application/shared candidate or mixed composition retained in place. This is
ownership guidance, not a claim that every listed import executes at startup.

| Root file | Class / reason | Local dependencies |
|---|---|---|
| `adaptive_question_selector.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_repair_evidence`, `knowledge_node_state_transition`, `prerequisite_backtrack_pilot`, `qualifications.pt.provider`, `question_bank`, `question_equivalence`, `short_term_repeat_guard` |
| `adaptive_source_mix.py` | C: PT policy/evidence or PT runtime composition | `question_bank` |
| `app.py` | D: application/shared candidate; preserve current composition | `adaptive_question_selector`, `database`, `goukaku_ui`, `knowledge_node_relations`, `learner_navigation_performance`, `learner_path_performance`, `learning_engine`, `learning_strategy_runtime_pilot`, `prerequisite_backtrack_pilot`, `question_bank`, `question_order_quality`, `short_term_repeat_guard`, `site_ui`, `written_understanding_check` |
| `companion_record.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_state_transition`, `question_equivalence` |
| `daily_wrong_review.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `dashboard_progress_trend.py` | C: PT policy/evidence or PT runtime composition | `database`, `field_evidence`, `field_progress` |
| `dashboard_read_bundle.py` | D: application/shared candidate; preserve current composition | `database`, `recommendation_daily_summary`, `trial100_store` |
| `dashboard_real_data_shadow.py` | C: PT policy/evidence or PT runtime composition | `field_evidence`, `field_progress`, `judgment_shadow` |
| `dashboard_settings.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `database.py` | D: application/shared candidate; preserve current composition | `question_bank` |
| `developer_access_recovery.py` | D: application/shared candidate; preserve current composition | `developer_ui`, `goukaku_ui` |
| `developer_status.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `developer_ui.py` | D: application/shared candidate; preserve current composition | `database`, `developer_status`, `email_delivery`, `feedback_store`, `goukaku_ui`, `knowledge_node_state_transition`, `phase11_intent_selection_alignment`, `phase11_promotion_gate_status`, `phase11_repair_effectiveness_facts`, `phase11_retention_horizon_facts`, `phase11_retention_outcome_audit`, `phase11_retention_supply_audit`, `phase11_session_load_facts`, `pilot_diagnostics`, `supporter_performance` |
| `durable_paused_session.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `durable_web_learning_session.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `email_delivery.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `exam_weight_shadow.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `feedback_store.py` | D: application/shared candidate; preserve current composition | `database` |
| `field_evaluation_shadow.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `field_evidence.py` | C: PT policy/evidence or PT runtime composition | `database`, `knowledge_node_canonical`, `knowledge_node_state_transition`, `knowledge_node_weakness_evidence`, `question_bank` |
| `field_learning_target_shadow.py` | C: PT policy/evidence or PT runtime composition | `exam_weight_shadow`, `field_evaluation_shadow`, `field_progress` |
| `field_progress.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `field_progress_presentation.py` | C: PT policy/evidence or PT runtime composition | `field_evidence`, `field_progress` |
| `goukaku_ui.py` | D: application/shared candidate; preserve current composition | `dashboard_read_bundle`, `dashboard_real_data_shadow`, `dashboard_settings`, `database`, `field_evidence`, `field_progress`, `field_progress_presentation`, `judgment_shadow`, `learner_path_performance`, `learner_readiness_presentation`, `learning_analysis`, `learning_milestones`, `overall_progress_presentation`, `pass_readiness`, `phase12_presentation`, `pilot_diagnostics`, `supporter_performance`, `supporter_report`, `trial100_store` |
| `initial_assessment_repeat_guard.py` | C: PT policy/evidence or PT runtime composition | `short_term_repeat_guard` |
| `judgment_shadow.py` | C: PT policy/evidence or PT runtime composition | `phase11_formal_judgment` |
| `knowledge_node_canonical.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `knowledge_node_relations.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `knowledge_node_repair_cycle.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_state_transition` |
| `knowledge_node_repair_evidence.py` | C: PT policy/evidence or PT runtime composition | `question_bank`, `question_equivalence` |
| `knowledge_node_repairability.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_canonical`, `knowledge_node_relations`, `knowledge_node_repair_evidence`, `question_bank` |
| `knowledge_node_state_transition.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_repair_evidence`, `knowledge_node_weakness_evidence`, `question_equivalence` |
| `knowledge_node_weakness_evidence.py` | C: PT policy/evidence or PT runtime composition | `question_equivalence` |
| `learner_navigation_performance.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `learner_path_performance.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `learner_readiness_presentation.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `learning_analysis.py` | C: PT policy/evidence or PT runtime composition | `question_bank` |
| `learning_engine.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_canonical`, `knowledge_node_state_transition`, `qualifications.pt.provider`, `question_bank`, `question_equivalence` |
| `learning_milestones.py` | C: PT policy/evidence or PT runtime composition | `dashboard_settings`, `knowledge_node_canonical`, `knowledge_node_state_transition` |
| `learning_strategy_context_shadow.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `learning_strategy_runtime_pilot.py` | C: PT policy/evidence or PT runtime composition | `adaptive_question_selector`, `field_evidence`, `field_progress`, `knowledge_node_state_transition`, `learning_strategy_context_shadow`, `learning_strategy_shadow`, `question_bank`, `question_equivalence`, `short_term_repeat_guard` |
| `learning_strategy_shadow.py` | C: PT policy/evidence or PT runtime composition | `field_learning_target_shadow` |
| `learning_time_guard.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `one_question_starter.py` | C: PT policy/evidence or PT runtime composition | `question_bank` |
| `overall_progress_presentation.py` | C: PT policy/evidence or PT runtime composition | `field_progress_presentation` |
| `pass_readiness.py` | C: PT policy/evidence or PT runtime composition | `field_evidence`, `field_progress`, `knowledge_node_canonical`, `knowledge_node_weakness_evidence`, `phase11_formal_judgment`, `question_bank` |
| `payment_access.py` | D: application/shared candidate; preserve current composition | `payment_entitlement` |
| `payment_entitlement.py` | D: application/shared candidate; preserve current composition | `database` |
| `phase11_active_field_facts.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_weakness_evidence` |
| `phase11_active_repair_rules.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `phase11_active_safety.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_weakness_evidence` |
| `phase11_active_weakness.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_repair_cycle`, `knowledge_node_weakness_evidence`, `question_equivalence` |
| `phase11_evaluable_nonrepair_rules.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `phase11_formal_judgment.py` | C: PT policy/evidence or PT runtime composition | `field_evidence`, `knowledge_node_canonical`, `knowledge_node_state_transition`, `phase11_active_field_facts`, `phase11_active_repair_rules`, `phase11_active_safety`, `phase11_active_weakness`, `phase11_evaluable_nonrepair_rules`, `phase11_retention_field_facts`, `question_bank` |
| `phase11_gate_ui.py` | C: PT policy/evidence or PT runtime composition | `database`, `developer_ui`, `knowledge_node_state_transition`, `phase11_intent_selection_alignment`, `phase11_promotion_gate_status`, `phase11_repair_effectiveness_facts`, `phase11_retention_horizon_facts`, `phase11_retention_outcome_audit`, `phase11_retention_supply_audit`, `phase11_session_load_facts`, `pilot_diagnostics` |
| `phase11_intent_selection_alignment.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_canonical`, `knowledge_node_repair_evidence`, `knowledge_node_state_transition` |
| `phase11_promotion_gate_status.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `phase11_repair_effectiveness_facts.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `phase11_retention_field_facts.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `phase11_retention_horizon_facts.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `phase11_retention_outcome_audit.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_canonical`, `knowledge_node_repair_evidence`, `knowledge_node_state_transition` |
| `phase11_retention_supply_audit.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_repair_evidence`, `knowledge_node_repairability` |
| `phase11_retrospective_shadow_audit.py` | C: PT policy/evidence or PT runtime composition | `field_evidence`, `judgment_shadow`, `question_bank` |
| `phase11_session_load_facts.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `phase12_presentation.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `pilot_diagnostics.py` | C: PT policy/evidence or PT runtime composition | `adaptive_question_selector`, `database`, `field_evidence`, `judgment_shadow`, `knowledge_node_canonical`, `knowledge_node_state_transition`, `knowledge_node_weakness_evidence`, `learning_analysis`, `phase11_active_weakness`, `phase11_retrospective_shadow_audit`, `question_bank`, `repairability_diagnostics` |
| `prerequisite_attempt_cache.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `prerequisite_backtrack.py` | C: PT policy/evidence or PT runtime composition | `prerequisite_diagnosis` |
| `prerequisite_backtrack_pilot.py` | C: PT policy/evidence or PT runtime composition | `prerequisite_backtrack`, `prerequisite_diagnosis` |
| `prerequisite_diagnosis.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `progress_shadow_audit.py` | C: PT policy/evidence or PT runtime composition | `database`, `field_evidence`, `field_progress` |
| `qualification_dashboard_scope.py` | C: PT policy/evidence or PT runtime composition | `qualifications.common.learning_store_registry` |
| `qualification_history_scope.py` | C: PT policy/evidence or PT runtime composition | `qualifications.common.learning_store_registry` |
| `qualification_learning_time_scope.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `qualification_learning_writer_scope.py` | C: PT policy/evidence or PT runtime composition | `qualifications.pt.learning_writer` |
| `question_bank.py` | C: PT policy/evidence or PT runtime composition | `question_equivalence` |
| `question_equivalence.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_canonical` |
| `question_order_quality.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `readiness_service.py` | C: PT policy/evidence or PT runtime composition | `database`, `field_evidence`, `field_progress`, `pass_readiness`, `trial100_store` |
| `recommendation_daily_summary.py` | D: application/shared candidate; preserve current composition | `database` |
| `repairability_diagnostics.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_canonical`, `knowledge_node_repair_evidence`, `knowledge_node_repairability`, `knowledge_node_state_transition` |
| `short_term_repeat_guard.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_state_transition`, `question_bank`, `question_equivalence` |
| `site_beta_copy.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `site_direct_line_cta.py` | D: application/shared candidate; preserve current composition | `site_marketing_refresh` |
| `site_legal_ui.py` | D: application/shared candidate; preserve current composition | `feedback_store` |
| `site_marketing_hotfix.py` | D: application/shared candidate; preserve current composition | `site_marketing_refresh` |
| `site_marketing_refresh.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `site_marketing_viewport_fix.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `site_seo_foundation.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `site_ui.py` | D: application/shared candidate; preserve current composition | `developer_ui`, `site_legal_ui`, `stripe_billing_ui`, `stripe_webhook_ui` |
| `stripe_billing_ui.py` | D: application/shared candidate; preserve current composition | `goukaku_ui`, `stripe_checkout_service` |
| `stripe_checkout_service.py` | D: application/shared candidate; preserve current composition | `payment_entitlement`, `stripe_entitlement_adapter` |
| `stripe_entitlement_adapter.py` | D: application/shared candidate; preserve current composition | `payment_entitlement` |
| `stripe_webhook_ui.py` | D: application/shared candidate; preserve current composition | `stripe_entitlement_adapter` |
| `supporter_learner_preview_bridge.py` | D: application/shared candidate; preserve current composition | `goukaku_ui` |
| `supporter_performance.py` | D: application/shared candidate; preserve current composition | No local Python import; contract/callers still matter |
| `supporter_report.py` | C: PT policy/evidence or PT runtime composition | `dashboard_settings`, `database`, `learning_analysis`, `supporter_performance` |
| `term_explainer.py` | C: PT policy/evidence or PT runtime composition | `question_bank` |
| `trial100_evidence.py` | C: PT policy/evidence or PT runtime composition | No local Python import; contract/callers still matter |
| `trial100_store.py` | D: application/shared candidate; preserve current composition | `database`, `trial100_evidence` |
| `written_understanding_check.py` | C: PT policy/evidence or PT runtime composition | `knowledge_node_canonical` |
| `wsgi.py` | D: application/shared candidate; preserve current composition | `app`, `daily_wrong_review`, `dashboard_progress_trend`, `database`, `developer_access_recovery`, `developer_ui`, `durable_paused_session`, `durable_web_learning_session`, `goukaku_ui`, `initial_assessment_repeat_guard`, `learning_time_guard`, `one_question_starter`, `phase11_gate_ui`, `prerequisite_attempt_cache`, `qualification_dashboard_scope`, `qualification_history_scope`, `qualification_learning_time_scope`, `qualification_learning_writer_scope`, `scripts.setup_rich_menu`, `site_beta_copy`, `site_direct_line_cta`, `site_marketing_hotfix`, `site_marketing_refresh`, `site_marketing_viewport_fix`, `site_seo_foundation`, `supporter_learner_preview_bridge`, `term_explainer` |
