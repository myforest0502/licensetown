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
| lower-page 優先課題 TOP3 (`dashboard.weak_fields`) | `build_learning_guidance(...)` legacy path | LEGACY INTERPRETATION | HIDE on formal learner page; retain fallback data for legacy callers |
| lower-page 今日のおすすめ学習 (`dashboard.recommended_study`) | `build_learning_guidance(...)` legacy path | LEGACY INTERPRETATION | HIDE on formal learner page; retain fallback data for legacy callers |
| 源さんの一言 | `build_gensan_comment(...)` using legacy fields/weak/recommended inputs | LEGACY/MIXED PRESENTATION | KEEP temporarily; later make formal-input aware |
| reward/milestone progress | saved answer-count reward calculation | FACTUAL/GAMIFICATION | RETAIN |

## Main inconsistency found

The page originally contained **two recommendation systems at once**:

1. top learner-navigation block: formal evidence and strategy intent;
2. lower `優先課題 TOP3` + `今日のおすすめ学習`: legacy `build_learning_guidance` output.

This could show different fields or different reasons on one page. The top formal CTA already carries field, question count, learning intent and reason code into the recommendation-start endpoint, so the lower legacy recommendation is not needed as an independent authority.

## Consolidation v0.1 implemented on `work/dashboard-formal-consolidation-v01`

The learner-page layout now detects the formal `.learner-navigation` block and, only when that formal block exists:

- removes the lower legacy `.weak-card`;
- removes the lower legacy `.recommend-card`;
- preserves factual counters, source data and legacy fallback structures in Python;
- leaves supporter/read-only/legacy contexts unchanged because the DOM change is conditional on formal learner navigation;
- if formal field-progress rows are not present yet, relabels the old subject percentage section from `分野別 到達度` to **`分野別 正答率（参考）`** so accuracy is not presented as formal attainment.

This is deliberately a small source-authority fix rather than a dashboard redesign.

## Field-progress inconsistency

`include_learner_navigation=True` forces formal overall-progress presentation, but **does not yet force formal field-progress UI**. Field-level display still depends on `ENABLE_FIELD_PROGRESS_UI`.

Until that backend activation is completed, the learner page no longer calls legacy per-field accuracy `到達度`; it is explicitly shown as reference accuracy only.

Target end state remains:
- formal overall progress based on coverage/state evidence;
- formal per-field progress based on the same evidence;
- accuracy shown separately as accuracy.

## Recommended minimal consolidation v0.2

1. Make formal field-progress presentation active on the signed learner route without silently changing supporter/read-only legacy behavior.
2. Keep ordinary accuracy visible as a sub-metric.
3. Preserve factual counters (answers/time/accuracy/streak); they are not competing strategy authorities.
4. Do not promote Phase11 merely because the dashboard uses formal navigation. Learner-facing strategy remains constrained by the existing promotion/feature-gate contract where applicable.
5. Keep `build_learning_guidance` available for legacy/supporter compatibility until every caller is mapped; do not delete it yet.

## Acceptance criteria

### v0.1
- Learner page never displays two conflicting recommended fields from formal and legacy systems.
- Legacy field accuracy is not mislabeled as formal attainment.
- Existing factual counters remain unchanged.
- Existing authentication and recommendation-start behavior remain unchanged.
- Supporter/read-only pages are not silently changed.
- Full regression suite remains green.

### final dashboard consolidation
- `分野別 到達度` on the learner page uses formal field-progress calculation, with accuracy clearly shown only as accuracy.
- One formal recommendation/priority authority remains learner-facing.
- Full regression suite remains green.

## Next implementation step

After v0.1 CI is green, integrate it into `work/pt-finalization-post-q2000`, then complete the small backend learner-route-only formal field-progress activation as v0.2.
