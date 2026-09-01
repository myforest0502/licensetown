# LicenseTown Phase 12 — 「合格への道」見える化 v0.1

Date: 2026-09-01
Status: design fixed / implementation not yet started

## 1. Purpose

Phase 12 turns LicenseTown's formal learning evidence and Phase 11 judgment into a learner-facing navigation view.

The page must answer, at a glance:

1. 今どこまで進んでいるか
2. 何が安定しているか
3. 何を修復中か
4. 何がまだ十分に確認できていないか
5. 今日、次に何をやるべきか
6. その理由は何か

This is not an examination pass probability screen. It must never claim a percentage probability of passing.

## 2. Existing dashboard assets to preserve

The current `/goukaku-no-michi` already has useful production UI and must not be rebuilt unnecessarily:

- exam date / countdown
- overall progress preview
- total answers / study time / recent accuracy / average accuracy / streak
- field progress preview
- weak field TOP3
- current daily recommendation
- recommendation progress
- Gensan comment
- reward / footprint / LINE actions

Phase 12 extends this surface rather than replacing it wholesale.

## 3. Evidence sources

Learner-facing Phase 12 may only use evidence already approved for formal learning state:

- question attempts
- canonical Knowledge Node state
- field evidence
- field progress
- retention / recheck_due state
- repeated weakness evidence
- Safety classification
- Phase 11 deterministic judgment
- current recommendation plan/progress

Do not use consultation text.
Do not use selector score as mastery.
Do not infer weakness from Question Bank distribution.

## 4. Phase 11 boundary

Phase 11 decides learning intent and scope.
Phase 10 continues to decide exact Q IDs.
Phase 12 visualizes the result.

Phase 12 must not:

- select exact Q IDs
- mutate Node state
- bypass Recent Cooldown
- create a second weakness/state model
- reinterpret AI text as formal repair evidence

## 5. v0.1 learner-facing information model

### A. Overall progress

Keep the existing overall progress model based on formal field/Node progress.

Display:

- overall progress
- coverage
- repair completed
- stable

Wording must clearly state this is learning progress, not pass probability.

### B. Current learning state summary

Add a compact state summary derived from formal canonical Node states:

- 未確認 / unseen
- 確認中 / checking
- 修復中 / repairing
- 修復済み / repaired
- 再確認待ち / recheck_due
- 定着 / stable

The learner does not need raw internal Node IDs.

### C. "いま直すところ"

Show up to three high-value current issues, prioritized by formal evidence:

1. critical Safety unresolved
2. confident wrong cluster
3. repeated wrong cluster
4. recheck_due
5. uncertain-correct stabilization

Do not label a field as weak from one ordinary wrong answer.

### D. "今日やること"

Phase 11 judgment becomes a learner-friendly action card.

Show:

- target field, or broad adaptive learning when target is None
- recommended question count
- learner-friendly reason
- action button using existing learning route

Internal reason codes and scores are not shown.

### E. "なぜこれをやるの？"

Expose a short evidence explanation without technical internals.

Examples:

- 「自信を持って間違えた内容が複数回確認されています」
- 「一度直した内容を、時間を空けて確認する時期です」
- 「まだ十分に取り組めていない分野です」
- 「迷いながら正解した問題が多く、定着確認が必要です」

Never expose priority_score, internal Node IDs, or developer comparison labels.

## 6. Promotion safety gate

Phase 11 Shadow is currently diagnostics-only.
Therefore Phase 12 v0.1 must be implemented behind a default-OFF feature flag before learner-facing promotion.

Proposed flag:

`ENABLE_PHASE12_GUIDANCE_PREVIEW`

Default: OFF.

When OFF:

- current learner dashboard behavior remains exactly unchanged
- current `build_learning_guidance()` recommendation remains authoritative

When ON in QA/explicit pilot:

- render Phase 12 preview card
- do not overwrite or delete current recommendation until promotion criteria are met
- clearly distinguish preview during pilot if necessary

## 7. Promotion criteria

Do not replace current learner-facing recommendation until all are true:

- Phase 10 natural-use audit persistence confirmed
- no unexplained recent-Q overlap
- no critical Safety miss in Phase 11 comparison set
- no repeated overreaction to single ordinary wrong answers
- recheck_due is not starved
- sparse learners receive appropriate coverage guidance
- Phase 11 intent is compatible with Phase 10 selector behavior
- natural-use comparison shows Phase 11 is at least as relevant and safer than current guidance

## 8. Implementation sequence

### Stage A — data adapter

Create a presentation adapter that converts Phase 11 output + field evidence into learner-facing data.

Suggested module:

`phase12_presentation.py`

Pure/read-only. No Flask, DB write, LLM, or exact Q selection.

Suggested output:

```python
{
    "enabled": True,
    "intent": "repair",
    "headline": "今日は精神医学を10問",
    "reason": "自信を持って間違えた内容を優先して確認します。",
    "target_field": "精神医学",
    "question_count": 10,
    "route": "dashboard_recommendation",
    "state_summary": {
        "checking": 12,
        "repairing": 4,
        "repaired": 20,
        "recheck_due": 3,
        "stable": 8,
        "unseen": 1462
    },
    "attention_items": [...]
}
```

### Stage B — dashboard wiring behind flag

In `goukaku_ui.build_dashboard()`:

- reuse attempts/evidence already loaded for progress where practical
- build current guidance as today
- build Phase 11 shadow judgment read-only
- build Phase 12 presentation only when preview flag is enabled

Avoid duplicate expensive full-bank calculations where possible.

### Stage C — template preview

Add one self-contained card to `templates/goukaku/home.html`.

Do not redesign the whole dashboard in v0.1.
Do not remove current recommendation card.
Do not alter existing action paths when flag is OFF.

### Stage D — supporter visibility

Read-only supporter view may show the same Phase 12 preview when the flag is enabled, because it uses `build_dashboard()`.
No action button in read-only mode.

## 9. Minimum tests

Presentation unit tests:

1. safety_repair -> correct learner wording
2. confident_wrong_cluster -> repair wording
3. repeated_wrong_cluster -> repair wording
4. recheck_due -> retention wording
5. insufficient_coverage -> coverage wording
6. uncertain_correct_cluster -> stabilization wording
7. maintenance_only -> broad adaptive wording
8. internal score/Node ID never exposed
9. state summary totals are deterministic

Integration/regression:

10. feature flag OFF => existing dashboard payload/render unchanged
11. feature flag ON => preview payload present
12. learner recommendation logic remains current baseline during preview
13. supporter read-only has no start control
14. no DB write added
15. no Node-state mutation
16. no selector/cooldown change
17. existing Phase 10/11 tests pass
18. full pytest
19. Question Bank validator

## 10. Definition of Phase 12 complete

Phase 12 is complete when:

- the learner can understand current learning progress without interpreting raw scores
- stable / repairing / recheck / unseen state is visible in understandable language
- the system tells the learner what to do next and why
- the recommended action routes into the existing study flow
- no pass-probability claim is made
- learner-facing promotion has passed the Phase 10/11 natural-use gate
- the result remains explainable and auditable from formal stored evidence
