# Dashboard source map — 2026-09-09

Scope: learner-facing `/goukaku-no-michi` on safe post-Q2000 branch.

Purpose: identify which visible cards are driven by formal derived evidence, ordinary factual aggregates, legacy guidance, or mixed sources before any consolidation change.

## Current rendering path

`/goukaku-no-michi` calls:

`build_dashboard(user_id, include_learner_navigation=True)`

This means the current learner page always builds the formal learner-navigation path and formal overall-progress presentation, while several older cards are still populated from the legacy guidance path.

Formal authority remains:

`question_attempts -> build_field_evidence -> build_field_progress / derived Node state -> dashboard_real_data_shadow / pass_readiness -> learner presentation`

Legacy learning summary/activity data remains useful for factual counters such as total answers, study time, streak and recent accuracy; the problem is not that all old data is invalid, but that **legacy recommendation/weakness interpretation still coexists with formal interpretation on the same page**.

## Visible card source map

| Visible area | Current source | Classification | Disposition |
|---|---|---|---|
| 現在地 | `learner_navigation` from formal attempts/readiness/shadow | FORMAL | RETAIN |
| 今日やること | `learner_navigation.today_action` | FORMAL | RETAIN as recommendation authority |
| 優先課題 TOP3 inside learner navigation | formal `attention_items` | FORMAL | RETAIN as priority authority |
| できていること / 直していること / 未確認 / 次の確認 | formal learner navigation | FORMAL | RETAIN |
| 試験日 / 残り日数 | dashboard settings | FACTUAL SETTINGS | RETAIN |
| 合格への到達度 | formal `overall_progress_preview` when learner navigation is included | FORMAL | RETAIN |
| 総回答数 | saved dashboard summary | FACTUAL AGGREGATE | RETAIN |
| 累計学習時間 | saved activity/time aggregate | FACTUAL AGGREGATE | RETAIN, with known session-link analysis limitation |
| 直近7日正答率 | saved dashboard summary | FACTUAL AGGREGATE | RETAIN |
| 平均正答率 | saved dashboard summary | FACTUAL AGGREGATE | RETAIN |
| 連続学習日数 | saved activity aggregate | FACTUAL AGGREGATE | RETAIN |
| 分野別 到達度 | formal only when `ENABLE_FIELD_PROGRESS_UI` is enabled; otherwise legacy field accuracy list | MIXED / FLAGGED | FORMALIZE |
| lower-page 優先課題 TOP3 (`dashboard.weak_fields`) | `build_learning_guidance(...)` legacy path | LEGACY INTERPRETATION | REPLACE/DEMOTE; duplicates formal TOP3 |
| lower-page 今日のおすすめ学習 (`dashboard.recommended_study`) | `build_learning_guidance(...)` legacy path | LEGACY INTERPRETATION | REPLACE with formal today action; currently duplicate authority |
| 源さんの一言 | `build_gensan_comment(...)` using legacy fields/weak/recommended inputs | LEGACY/MIXED PRESENTATION | KEEP temporarily; later make formal-input aware |
| reward/milestone progress | saved answer-count reward calculation | FACTUAL/GAMIFICATION | RETAIN |

## Main inconsistency found

The page currently contains **two recommendation systems at once**:

1. top learner-navigation block: formal evidence and strategy intent;
2. lower `優先課題 TOP3` + `今日のおすすめ学習`: legacy `build_learning_guidance` output.

This can show different fields or different reasons on one page. The top formal CTA already carries field, question count, learning intent and reason code into the recommendation-start endpoint, so the lower legacy recommendation is no longer needed as an independent authority.

## Field-progress inconsistency

`include_learner_navigation=True` forces formal overall-progress presentation, but **does not force formal field-progress UI**. Field-level display still depends on `ENABLE_FIELD_PROGRESS_UI`.

Therefore a learner can currently see:
- formal overall progress based on coverage/state evidence;
- legacy per-field accuracy bars labeled as `分野別 到達度` when the field-progress flag is off.

That is semantically inconsistent. Accuracy is useful, but it is not the same thing as formal field progress.

## Recommended minimal consolidation v0.1

Do not redesign the whole dashboard at once.

1. When `learner_navigation_enabled=True`, make formal field-progress presentation active as well. Keep ordinary accuracy visible as a sub-metric.
2. Replace the lower legacy `優先課題 TOP3` content with the same formal `attention_items` already used by learner navigation, or hide the duplicate lower block. Prefer one recommendation authority.
3. Replace lower `今日のおすすめ学習` with `learner_navigation.today_action` when formal navigation exists. Legacy recommendation remains fallback only for non-formal/read-only legacy contexts.
4. Preserve factual counters (answers/time/accuracy/streak); they are not competing strategy authorities.
5. Do not promote Phase11 merely because the dashboard uses formal navigation. Learner-facing strategy remains constrained by the existing promotion/feature-gate contract where applicable.
6. Keep `build_learning_guidance` available for legacy/supporter compatibility until every caller is mapped; do not delete it in this first change.

## Acceptance criteria for consolidation change

- Learner page never displays two conflicting recommended fields from formal and legacy systems.
- `分野別 到達度` on the learner page uses formal field-progress calculation, with accuracy clearly shown only as accuracy.
- Existing factual counters remain unchanged.
- Existing authentication and recommendation-start behavior remain unchanged.
- Supporter/read-only pages are not silently changed unless explicitly covered by tests.
- Full regression suite remains green.

## Next implementation step

Create a small learner-page-only consolidation change on `work/dashboard-formal-consolidation-v01`, add regression tests for source authority, run targeted dashboard tests, then full CI before any safe-branch integration.
