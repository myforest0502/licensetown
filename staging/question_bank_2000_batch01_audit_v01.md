# Question Bank 2000 — Batch 01 staging audit v01

Date: 2026-09-08

## Scope

This audit is for content staging only. No Q IDs are reserved, no Question Bank JSON is changed, no Knowledge Node is created or rewritten, no DB/Production write occurs.

Baseline: main after PR #262 (`6ebfcc7c32cccc307b239f1000a311d4a606c34b`).

The 2000-question gap audit recommends starting with a small 8–12 item lot around high-priority clinical areas and existing repair supply. Batch 01 therefore calibrates 12 accepted drafts before any bank integration.

## Structural result

- Draft records produced: 13 total candidate records (12 in main staging file + 1 replacement).
- Accepted for Batch 01 calibration count: 12.
- HOLD: B01-05 / KN0025, because the current registry already marks KN0025 `confirmed_shared` with Q25/Q1596/Q1608. It is not needed for the first singleton-first lot. It may be reconsidered later only as a deliberate third-demand multi reinforcement.
- Replacement accepted: B01-R1 / KN0028, which is a singleton target in the current registry.
- No duplicate target Node among the 12 accepted records.
- KN0779 is not used.
- No new Node is proposed in Batch 01.
- No Q number is preallocated.

Accepted set:

1. B01-01 — KN0011 — 自律神経過反射への初期対応
2. B01-02 — KN0033 — 鶏歩へのAFO適応
3. B01-03 — KN0023 — 視覚・体性感覚を利用した協調運動/歩行練習
4. B01-04 — KN0013 — 易疲労性を踏まえた運動配慮
5. B01-06 — KN0026 — 過用を避けた中等度運動
6. B01-07 — KN0024 — 感覚低下と暗所歩行不安の評価
7. B01-08 — KN0031 — 日常生活場面の左側注意低下
8. B01-09 — KN0032 — PROM/AROM差と肩甲骨代償
9. B01-10 — KN0009 — 後上方インピンジメント
10. B01-11 — KN0016 — 神経性間欠性跛行
11. B01-12 — KN0027 — 手根管症候群/正中神経障害
12. B01-R1 — KN0028 — 無痛性皮膚障害の自己管理

## Content quality checks

### Passed at staging level

- Every accepted stem has one intended best answer.
- Every accepted choice has an explicit reason.
- No item is a pure vocabulary-only addition; each uses a finding, safety decision, assessment choice, device choice, or intervention choice.
- The batch contains multiple Safety-relevant decisions without making every item a Safety item.
- Stems are short enough for LINE use and do not intentionally add irrelevant history.
- Distractors are medically related to the decision space and are not random words.
- Each accepted item attempts a different demand from the existing Node label where possible, to support future STRONG repair evidence instead of same-demand paraphrase.

### Requires integration-time validation

The staging connector cannot safely treat proposed category numbers as authoritative without reading the exact current question/tag record for each reference Q. Therefore `proposed_category_*` remains provisional and `category_validation_required=true` is intentionally preserved.

Before a draft is promoted into the formal bank, integration must confirm all of the following from the current four stores:

- exact existing reference question text and choices;
- existing task / primary ability / level / Safety;
- exact category_small/category_large;
- Node canonical resolution and singleton/multi status at integration time;
- semantic independence from the existing question, not merely a changed vignette;
- no near-duplicate with any other bank question;
- accepted answer and all distractor explanations remain medically correct after wording normalization.

A mismatch does not get silently fixed by changing the existing record. The new draft is either revised to fit the existing canonical Node or moved to HOLD.

## Per-draft audit

| Draft | Structural status | Content status | Main note |
|---|---|---|---|
| B01-01 | ACCEPT | ACCEPT | Critical Safety decision; keep acute hypertension + headache context. |
| B01-02 | ACCEPT | ACCEPT | Device choice requires gait interpretation; avoid reducing to “下垂足=AFO” wording during integration. |
| B01-03 | ACCEPT | ACCEPT | Feedback response is used to justify intervention; preserve accuracy-over-speed emphasis. |
| B01-04 | ACCEPT | ACCEPT | Fatigue dosing rather than disease-name recall. |
| B01-05 | HOLD | CONTENT-OK / LOW-PRIORITY | KN0025 already confirmed_shared; do not count in singleton-first 12. |
| B01-06 | ACCEPT | ACCEPT | Delayed fatigue is used as a load-adjustment cue; avoid disease-specific claims not present in stem. |
| B01-07 | ACCEPT | ACCEPT | Sensory context interpretation; category must be checked. |
| B01-08 | ACCEPT | ACCEPT | Moves from ADL observation to targeted assessment selection. |
| B01-09 | ACCEPT | ACCEPT | PROM/AROM discrepancy leads to motor-control intervention; retain postoperative safety context when integrated. |
| B01-10 | ACCEPT | ACCEPT | Movement-position application rather than term recall. |
| B01-11 | ACCEPT | ACCEPT | Uses flexion-relief pattern to choose tolerable aerobic modality. |
| B01-12 | ACCEPT | ACCEPT | Different demand from prognosis: lesion localization. Keep as Level 2 bridge item, not a high-level reasoning item. |
| B01-R1 | ACCEPT | ACCEPT | Replaces B01-05 for singleton-first count; concrete skin protection decision. |

## Batch 01 mix (accepted 12)

Proposed task mix:

- safety_priority: 3
- intervention_selection: 4
- device_selection: 1
- finding_interpretation: 3
- assessment_selection: 1

Proposed level mix:

- Level 2: 7
- Level 3: 5
- Level 1: 0
- Level 4: 0

Proposed Safety mix:

- critical: 1
- moderate: 8
- none: 3

This is a calibration lot, not the final +257 distribution. It does not need to mirror the full allocation exactly.

## Promotion rule for the next step

Batch 01 can move from `staging_only` to formal-bank integration only after exact current-record comparison is automated or otherwise reproducibly performed. Formal integration must update questions/answers/explanations/question_tags/Node metadata together and revise the manifest/schema range contract in the same controlled branch; partial store writes are not acceptable.

Until that step, these drafts are intentionally isolated from runtime and Production.
