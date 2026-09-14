# Stage F.2 Recommendation Plan replay — 2026-09-14

**PASS WITH CONDITIONS / YES FOR SEPARATE PROMOTION REVIEW.**
Base main: 076df39b142c1f08f520a8c1f55b211c688d80db. PR #351 is audit/tests/docs only.
Production authority remains false. This acceptance permits default-OFF pilot
integration preparation, not activation or a claim of educational effectiveness.

## Observed source and limits

Production project/default branch reverified: licensetown,
sparkling-frost-71060602 / production / br-raspy-pond-azxss69f. SELECT only.
Latest export: 2655 PT attempts, 14 plans, 20 complete ten-answer web sessions.
Learner selection is internal (most PT attempts); no identifier/event key exported.
The private anonymous input stays outside Git. Plan reason/intent missing in the
first three records remains null. Exact input timestamps and aggregate results
are retained in the companion JSON, without attempts or learner identifiers.

Reproduce with DATABASE_URL empty, PYTHONPATH=.:
`python -B scripts/audit_recommendation_plan_shadow.py /private/input.json /private/output.json`.
Input has attempts (Stage F schema), plans (answered_at, field, goal, reason_code,
learning_intent), sessions (started_at, completed_at, answer_events, answered_count,
min_position, max_position). Sessions are SELECT aggregates grouped internally by
web-recommendation event-key session prefix, mode study, qualification pt; only
numeric answer suffixes are counted. All 20 sessions have positions1..10/count10
and dashboard_recommendation source tags. No general study batches are counted.

Recount differs from the supplied older summary: plan3 has **10**, not30,
explicit web recommendation answers; plan14 now has **20**, not10 (new session).
The plan3 interval also contains generic study batches, which are not counted as
recommendation completions. This changes neither the physiology five-plan streak
nor its pre-decision context. The earlier #351 fixture remains a prior supplied
aggregate scenario, not a current Production extraction claim.

Each ranking uses attempts strictly before its plan timestamp, the unchanged
Node/evidence/progress/B/D/E truth path, and formal bank field mapping. Prior
progress/stable ratio comes from the preceding plan checkpoint; elapsed study
uses last observed field answer. #349 supplies context only for the actual-plan
field. Other-field concentration, additional completed weakness blocks and
individual exam timing remain unavailable. No future completions enter ranking.
Session completion requires a full ten-answer session entirely inside the interval;
partial/straddling sessions are not credited. Goal is never used as completion.

## Fourteen decisions

| plan | UTC timestamp | actual | complete after | blocks before | Shadow top3 | intent | actual-field penalty | top1 supply |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-01T10:10:19.698000+00:00 | 人間発達学 | 10 | 0 | 理学療法治療各論 / 生理学 / 解剖学 | coverage | 0.000 | 327 |
| 2 | 2026-09-01T23:10:15.112000+00:00 | 小児学 | 10 | 0 | 理学療法治療各論 / 生理学 / 解剖学 | coverage | 0.000 | 325 |
| 3 | 2026-09-02T23:07:59.546000+00:00 | 神経医学 | 10 | 0 | 理学療法治療各論 / 生理学 / 解剖学 | coverage | 0.000 | 324 |
| 4 | 2026-09-03T23:18:12.250000+00:00 | 基礎運動学 | 20 | 0 | 神経医学 / 病理学 / 理学療法治療各論 | safety_review | 0.000 | 129 |
| 5 | 2026-09-05T06:59:06.040000+00:00 | 生理学 | 10 | 0 | 神経医学 / 病理学 / 理学療法治療各論 | safety_review | 0.000 | 129 |
| 6 | 2026-09-05T23:00:51.864000+00:00 | 生理学 | 10 | 0 | 病理学 / 神経医学 / 理学療法治療各論 | safety_review | 0.000 | 46 |
| 7 | 2026-09-06T23:23:27.092000+00:00 | 生理学 | 10 | 0 | 病理学 / 神経医学 / 理学療法治療各論 | safety_review | 0.000 | 48 |
| 8 | 2026-09-07T23:07:47.887000+00:00 | 生理学 | 20 | 1 | 生理学 / 病理学 / 神経医学 | safety_review | 0.333 | 95 |
| 9 | 2026-09-08T23:08:22.914000+00:00 | 生理学 | 10 | 1 | 生理学 / 病理学 / 神経医学 | safety_review | 0.333 | 91 |
| 10 | 2026-09-09T23:54:42.804000+00:00 | 神経医学 | 40 | 0 | 生理学 / 病理学 / 神経医学 | safety_review | 0.000 | 86 |
| 11 | 2026-09-10T23:36:03.738000+00:00 | 病理学 | 10 | 0 | 生理学 / 病理学 / 理学療法治療各論 | safety_review | 0.000 | 41 |
| 12 | 2026-09-11T23:28:24.192000+00:00 | 病理学 | 10 | 0 | 生理学 / 病理学 / 内科学 | safety_review | 0.000 | 35 |
| 13 | 2026-09-12T23:02:00.596000+00:00 | 内科学 | 10 | 0 | 内科学 / 生理学 / 運動器 | safety_review | 0.000 | 102 |
| 14 | 2026-09-13T23:06:11.696000+00:00 | 内科学 | 20 | 0 | 内科学 / 生理学 / 運動器 | safety_review | 0.000 | 57 |

Top1 agreement4/14 (28.6%); top3 agreement7/14 (50%). Agreement is descriptive,
not an acceptance threshold. Actual longest run: physiology5 plans, goal50,
completed60 questions =2 completed30-question blocks after the run.
At its five decision times: blocks0,0,0,1,1. Top1: neurology, pathology, pathology,
physiology, physiology. Physiology penalty0,0,0,1/3,1/3; the last two scores each
fall by0.066667 versus the identical snapshot without concentration context.
Two unresolved critical Safety Nodes remain at each of those final two decisions;
the reason codes also show high exam weight/attainment gap. Continuation is
consistent with Safety's separate priority tier, not a disabled penalty.

## Acceptance

- Small-bank raw result from Stage B itself: psychology29 supply/120 answers and
  pediatrics58 supply/73 answers both assessing. No audit-side relabeling.
- Safety contradictions0/14; eligible30 supply14/14, minimum35, without relaxed
  cooldown, exact-equivalence or field fill. This is field-level supply, not proof
  of thirty Safety-specific strong-repair questions.
- Latest post-#337 history:645 attempts, same-Q/exact-evidence/cross-Q exact repeats
  under72h all0. Existing repeat/selector code unchanged.
- No observed plan-time context exceeds1 completed block. Thus no unexplained
  >3-block persistence is observed, but behavior at that exposure is not empirically
  proven. Repeated shadow checkpoint recommendations are not completed blocks.
- All recommended fields have high repository Exam Weight; no low-weight mild-weak
  domination. Reasons/components are fully retained in JSON for inspection.

Conditions: single-learner retrospective evidence is not prospective educational
benefit or coverage noninferiority. Additional weakness-block count remains unknown;
other-field context is partial. Pilot preparation must preserve all existing
selector safety, use explicit opt-in, default OFF, and fallback on unavailable
context or supply. No automatic activation. Phase11 remains HOLD/shadow only.

## Validation

Targeted replay/context/B/D/E tests:48 passed. Full suite, validator and exact
PR/main CI/deploy results are recorded in the delivery completion report. No
Production Python caller imports the audit script. Runtime preparation, if
performed, belongs in a separate PR from this audit.
