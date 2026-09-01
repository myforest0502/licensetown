# LicenseTown Phase 12 — 「合格への道」見える化 v0.1

Date: 2026-09-02
Status: implementation complete / preview pilot active / learner-facing replacement not promoted

## 1. Purpose

Phase 12 turns LicenseTown's formal learning evidence and Phase 11 judgment into a learner-facing navigation view.

The page should answer, at a glance:

1. 今どこまで進んでいるか
2. 何が安定しているか
3. 何を修復中か
4. 何がまだ十分に確認できていないか
5. 今日、次に何をやるべきか
6. その理由は何か

This is not an examination pass-probability screen. It must never claim a percentage probability of passing.

## 2. Existing dashboard assets preserved

`/goukaku-no-michi` continues to preserve the existing production surface:

- exam date / countdown
- overall progress preview
- total answers / study time / recent accuracy / average accuracy / streak
- field progress preview
- weak field TOP3
- current daily recommendation
- recommendation progress
- Gensan comment
- reward / footprint / LINE actions

Phase 12 is additive during preview. It does not replace the baseline recommendation.

## 3. Approved evidence sources

Phase 12 uses only approved formal evidence:

- question attempts
- canonical Knowledge Node state
- field evidence
- retention / recheck_due state
- repeated weakness evidence
- Safety classification
- Phase 11 deterministic judgment
- current recommendation data already present on the dashboard

Do not use consultation text.
Do not use selector score as mastery.
Do not infer learner weakness from Question Bank distribution.

## 4. Phase boundaries

- Phase 11 decides learning intent and scope.
- Phase 10 decides exact Q IDs and owns Recent Cooldown.
- Phase 12 presents the result in learner-friendly language.

Phase 12 must not:

- select exact Q IDs
- mutate Node state
- bypass Recent Cooldown
- create a second weakness/state model
- reinterpret AI prose as formal repair evidence

## 5. Implemented v0.1 information model

### A. State summary

`phase12_presentation.py` presents the six formal states deterministically:

- unseen
- checking
- repairing
- repaired
- recheck_due
- stable

Internal Node IDs are not exposed to the learner.

### B. 「いま直すところ」

The presentation adapter maps formal Phase 11 reasons into learner-friendly attention wording for:

- safety_repair
- confident_wrong_cluster
- repeated_wrong_cluster
- recheck_due
- uncertain_correct_cluster

No field is labeled weak merely because of one ordinary wrong answer.

### C. 「今日やること」

The preview uses Phase 11 output to display:

- target field, or broad recommended learning if no target field exists
- question count
- learner-friendly reason
- recommended route identifier

The existing baseline recommendation remains authoritative during preview.

### D. 「なぜこれをやるの？」

Current wording is deterministic and deliberately non-technical, for example:

- 「安全に関わる重要な内容を優先して確認します。」
- 「自信を持って間違えた内容が複数確認されています。」
- 「一度直した内容を、時間を空けて確認する時期です。」
- 「まだ十分に取り組めていない分野を広げます。」

Priority scores, Node IDs, comparison labels, and developer evidence are not exposed.

## 6. Implementation status

### Stage A — presentation adapter — COMPLETE

Implemented module:

`phase12_presentation.py`

Properties:

- pure/read-only
- no Flask dependency
- no DB write
- no LLM
- no exact-Q selection
- deterministic wording

### Stage B — dashboard wiring behind flag — COMPLETE

`goukaku_ui.build_dashboard()` supports:

`ENABLE_PHASE12_GUIDANCE_PREVIEW`

When the flag is OFF:

- Phase 12 preview payload is absent
- baseline recommendation remains unchanged

When the flag is ON:

- attempts and field evidence are read
- Phase 11 shadow judgment is built read-only
- Phase 12 presentation is added to the dashboard
- baseline recommendation remains in place

### Stage C — template preview — COMPLETE

Phase 12 is rendered additively in the existing dashboard template. It does not replace the existing recommendation card during pilot.

### Stage D — supporter visibility — COMPLETE

Supporter views reuse the same `build_dashboard()` path in read-only form.

A dedicated supporter learner-preview route also exists:

`/supporter/goukaku-no-michi/learner-preview`

This allows display QA without impersonating the learner or writing learning activity.

## 7. QA completed so far

Completed checks include:

- feature flag OFF preserves baseline behavior
- feature flag ON adds preview data
- presentation reason mappings are deterministic
- internal Node IDs / selector scores are not exposed
- no DB migration
- no Production DB write added by Phase 12
- no selector change
- no Node-state change
- no Phase 10 policy change
- supporter read-only rendering
- supporter learner-view preview for display QA

PC supporter and smartphone visual QA have been completed for the preview surface.

## 8. Current limitation discovered by real diagnostics

Phase 12 correctly reflected the formal state model, but diagnostics showed that `repairing -> repaired` was structurally difficult because strong different-Q evidence supply was extremely sparse.

Before the repair-supply pilot, a Production learner snapshot showed:

- repairing Nodes: 135
- strong different-Q available: 1
- weak different-Q only: 5
- same-Q / formally blocked: 129

This was a Question Bank evidence-supply limitation, not a Phase 12 rendering bug.

Q1595-Q1605 subsequently added eleven strong different-Q Safety repair alternatives. Static validation confirms all eleven source/new pairs are formal strong candidates. Actual `repaired` progress still depends on natural learner responses; Phase 12 must not infer repair merely because supply exists.

## 9. Phase 10 / Phase 11 gate status

Phase 10 is now operationally closed:

- Recent Cooldown v0.2 is on main
- adaptive audit persistence was confirmed in natural use
- observed recent overlaps were explained by legitimate Safety singleton supply shortage
- those eight Safety Nodes were verified to have no non-recent strong alternate at the time
- current Question Bank audit is valid through Q1605

Phase 11 remains diagnostics-only for learner recommendation authority. Its comparison is now symmetric: the baseline target and Shadow target receive the same formal J1→J7 evidence profile, and either side can have stronger formal evidence.

Phase 12 therefore remains a preview presentation of Shadow guidance; it is not yet the authoritative replacement for the baseline recommendation.

## 10. Promotion criteria still required

Do not replace the current learner-facing recommendation until natural-use evidence supports all of the following:

- no critical Safety miss
- no repeated overreaction to one ordinary wrong answer
- sparse learners receive appropriate coverage guidance
- recheck_due is not starved when such Nodes naturally exist
- Phase 11 intent is compatible with Phase 10 exact selection
- disagreements are reviewed symmetrically, including cases where current guidance is stronger
- adaptive unexplained repeats remain absent or are understood and corrected
- limited pilot shows Phase 11 guidance is at least as relevant and safe as baseline guidance

A single favorable Shadow example is insufficient for promotion.

See:

`docs/phase11-promotion-evidence-matrix.md`

## 11. Definition of Phase 12 v0.1 implementation complete

The implementation portion of Phase 12 v0.1 is complete because:

- formal state is translated into understandable learner language
- the system can show what to do next and why
- the preview is additive and feature-flagged
- it remains auditable from formal stored evidence
- no pass-probability claim is made
- supporter/read-only QA paths exist

Learner-facing recommendation replacement is a separate Phase 11 promotion decision and is not implied by Phase 12 implementation completeness.
