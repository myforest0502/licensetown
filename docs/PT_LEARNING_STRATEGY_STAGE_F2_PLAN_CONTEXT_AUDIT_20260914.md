# Stage F.2 recommendation-plan concentration audit — 2026-09-14

**Judgment: PASS WITH CONDITIONS. Production connection: NOT YET.**

This follow-up narrows the concentration-related HOLD reason from Stage F. It does not promote Stage D/E, does not connect Shadow strategy to Production selection or UI, and does not write to Production DB.

## Scope

Production was inspected with SELECT only. The PT learner with the largest natural history remains internally selected without exposing a learner identifier. Fourteen `recommendation_plan` events were observed. Every plan had `goal=10`.

Observed plan fields in order:

1. 人間発達学
2. 小児学
3. 神経医学
4. 基礎運動学
5. 生理学
6. 生理学
7. 生理学
8. 生理学
9. 生理学
10. 神経医学
11. 病理学
12. 病理学
13. 内科学
14. 内科学

The number of dashboard-recommendation questions actually completed after each plan and before the next plan was:

`10, 10, 30, 20, 10, 10, 10, 20, 10, 40, 10, 10, 10, 10`

These are observed completions, not plan goals.

## Concentration result

PR #349 introduced `derive_recommendation_plan_context()`, which computes recommendation-time context before adding work completed after that plan. This prevents future-completion leakage and never treats `goal` as completion evidence.

The longest same-field plan streak was 生理学, five recommendation plans. Its observed completion sequence was:

`10 -> 10 -> 10 -> 20 -> 10`

At the five recommendation decision points, the derived `consecutive_field_blocks` values are therefore:

`0 -> 0 -> 0 -> 1 -> 1`

The same-field completed-question counts visible before those decisions are:

`0 -> 10 -> 20 -> 30 -> 50`

After the final physiology plan, the observed same-field completion total reaches 60 questions, or two 30-question equivalents. **No observed recommendation decision occurs with three completed same-field 30-question blocks already behind it.** Across all 14 plans, the maximum recommendation-time `consecutive_field_blocks` is 1.

This means the original Stage F metric of 26 consecutive 30-answer checkpoints must not be interpreted as 26 completed learning blocks. That metric described repeated Shadow recommendations on retrospective checkpoints, not learner-completed recommendation blocks.

## Stage E concentration semantics

Stage E applies:

`concentration_penalty = clamp(consecutive_field_blocks / 3)`

and subtracts up to 0.20 from the non-Safety priority score. Critical Safety remains a separate top tier and is intentionally not suppressed by fatigue/concentration penalty.

With the observed Production recommendation history, the only repeated sequence reaching a non-zero recommendation-time penalty is the latter part of the physiology streak, where `consecutive_field_blocks=1`. The 3-block maximum concentration penalty threshold was not naturally reached in these 14 plans.

Existing tests already verify that concentration context lowers ordinary priority and that critical Safety can override it. The Stage F.2 regression test now also locks the observed anonymous 14-plan aggregate and confirms the physiology context `[0,0,0,1,1]`.

## Small-bank issue

The independent Stage F small-bank conflict was fixed in PR #348. Fields whose formal bank supply is below the 60-answer classification floor remain `assessing`; repeated answers cannot promote them to `weak` or `strong` solely by crossing 60 lifetime answers. Critical Safety can still receive priority while a field is assessing.

## Safety / supply / repeat evidence retained from Stage F

This follow-up does not change the earlier acceptance evidence:

- Safety priority contradictions: 0/85 Stage F checkpoints.
- Eligible 30-question field supply: 85/85 checkpoints; minimum observed eligible supply 34.
- Post-#337 natural history: 72-hour same-Q repeats 0, exact-evidence repeats 0, cross-Q exact repeats 0.
- #342 coverage-aware exploration remains unchanged.

## Why PASS WITH CONDITIONS rather than full PASS

The concentration-specific HOLD reason is materially reduced: the observed recommendation history does not show a recommendation decision after three completed same-field 30-question blocks, and the previously cited 26-checkpoint streak was not a valid completed-block count.

However, this is still retrospective evidence from one learner. Historical generic recommendation sessions cannot prove `additional_blocks_completed` under the Stage D post-weakness contract, so that value remains unavailable rather than inferred. The audit also does not create a counterfactual future showing what would have happened if the learner had followed every Stage E Shadow recommendation.

Therefore:

- **Stage F.2 judgment: PASS WITH CONDITIONS**
- **Production connection recommendation: NOT YET**
- A separate promotion review remains required before `selection_authority` can change.

Recommended next gate: run Shadow prospectively alongside natural use, persist/observe explicit strategy context without changing learner-facing selection, and verify that concentration, Safety, eligible supply, and coverage remain acceptable across new completed blocks.
