# Primary learner history analysis — 2026-09-09

Scope: read-only analysis of the primary learner's Production `question_attempts` history. No Production write, Render change, LINE change, or `main` mutation was performed.

## Snapshot

- Attempts: **1525**
- Correct: **1103**
- Overall accuracy: **72.3%**
- Unique questions: **740**
- Unique raw Knowledge Nodes: **572**
- Observation window: 2026-08-17 through 2026-09-09 JST

This is already large enough to use as the main retrospective real-use dataset for deciding what LicenseTown PT still needs. It should not be replaced by a small artificial beta dataset.

## Confidence calibration

| Confidence | Attempts | Correct | Accuracy |
|---|---:|---:|---:|
| 1 | 850 | 752 | 88.5% |
| 2 | 623 | 338 | 54.3% |
| 3 | 42 | 13 | 31.0% |
| missing/unknown | 10 | 0 | 0.0% |

### Interpretation

Confidence is strongly informative. The learner clearly separates "I know this" from "I am unsure" in a way that correlates with actual performance.

- Confidence-1 wrong answers: **98**. These are high-value misconception/repair candidates because the learner believed the answer was known.
- Confidence-2/3 correct answers: **351**. These are not equivalent to stable mastery; they are useful checking/retention candidates.

Therefore confidence should remain a first-class input to weakness/repair strategy. Removing or flattening confidence would discard valuable learner-state information.

## Repeat behavior

Across 740 unique questions:

- Questions attempted at least twice: **344**
- Repeat attempts beyond the first attempt: **785**
- First wrong -> latest correct: **76 questions**
- First correct -> latest wrong: **52 questions**
- First wrong -> latest wrong: **37 questions**
- First correct -> latest correct: **179 questions**

### Interpretation

A large part of actual use is already longitudinal rather than one-shot testing. This is useful evidence for repair and retention logic.

However, raw repeat count must not be interpreted as a defect by itself. Existing adaptive-repeat audit work already distinguishes justified spaced repeats, cooldown bypasses, non-adaptive repeats and historical rows without audit metadata. The important metric is whether repeated evidence changes learner state appropriately and whether gratuitous repeats are avoided.

The 37 still-wrong repeated questions and the 52 correct-to-wrong regressions are especially valuable for identifying persistent weakness and forgetting.

## Daily use pattern

The learner's ordinary use ranges from 5 to 200 answers per study day. Recent heavy-use days include 90, 105, 110, 130 and 200 attempts.

Accuracy varies materially by day rather than simply improving with volume. Examples include:

- 2026-08-24: 30 attempts, 46.7%
- 2026-09-02: 90 attempts, 83.3%
- 2026-09-05: 130 attempts, 63.8%
- 2026-09-06: 200 attempts, 74.5%
- 2026-09-08: 115 attempts, 83.5%

This supports using learner-state and confidence evidence rather than a simplistic rule such as "more questions = stronger state".

## Session/fatigue analysis limitation discovered

`attempt_position` currently resets within the 5-question batch. All 1525 rows fall in positions 1-5, so the present table cannot independently measure accuracy deterioration across positions 1-30 of a 30-question session.

Therefore a claimed "question 25-30 fatigue effect" cannot currently be derived from `question_attempts` alone.

This confirms the existing lower-priority architecture note: if session-level time/fatigue analysis becomes important, an explicit durable session relationship (`session_id` / `learning_event_key`) is needed. Do not add it merely for architectural neatness; add it only if the analysis becomes useful enough to change learner behavior.

## Product conclusions from the 1525-attempt history

### 1. Do not expand the Question Bank above Q2000 merely to add volume

The limiting issue is no longer raw question count. The learner has used only 740 unique questions while generating 1525 attempts. The higher-value work is deciding what to present, when to repair, when to recheck, and how to explain the next action.

### 2. Confidence-aware repair is justified by real data

The difference between confidence levels is large enough to support separate treatment:

- confidence-1 wrong -> misconception/high-priority repair;
- confidence-2/3 correct -> uncertain knowledge/checking rather than stable mastery;
- confidence-2/3 wrong -> ordinary weak evidence, strengthened by repetition/cross-question confirmation.

This matches the direction of the existing formal strategy/Node-state design.

### 3. Longitudinal companion record has real value

The dataset already contains transitions such as wrong -> correct, correct -> wrong and still wrong. A useful companion record should summarize these educational episodes rather than dump raw logs.

Minimum useful episode shape:

- Knowledge Node / learner-facing concept
- first meaningful weakness evidence
- why it was prioritized (confident wrong / repeated wrong / Safety etc.)
- repair question/evidence
- repair result
- later retention/regression result
- current state

### 4. Phase11 should remain evidence-gated, not blocked by lack of historical data

There is plenty of retrospective history for weak/repair/repeat analysis. The remaining OPEN Phase11 gates are specifically prospective/natural phenomena that cannot be manufactured from older data, especially spaced retention, first natural `recheck_due` execution, and comparison diversity.

### 5. Dashboard decision authority should stay formal

Because confidence and longitudinal transitions materially change interpretation, simple field accuracy cannot be the recommendation authority. Accuracy remains useful as a factual display, but the "what should I do next" decision should come from formal derived evidence.

## Priority after this analysis

1. Keep Phase11 Shadow-only while natural retention/recheck evidence accumulates.
2. Build the smallest useful longitudinal companion-record derivation from existing `question_attempts`; no new DB table is required for the first version.
3. Use the derived record to support learner/supporter summaries and to audit whether repair actually persists.
4. Add session/time linkage only if a later decision genuinely requires fatigue/time-efficiency analysis.
5. After the major product changes are integrated, use roughly 100-200 new ordinary attempts as a post-change acceptance sample rather than restarting validation from zero.

## Completion judgment

The 1525-attempt dataset is sufficient to stop treating "real-user validation" as an unknown. It already gives strong evidence about confidence calibration, repeat/repair behavior and the need for longitudinal state interpretation.

The remaining validation gap is narrower: **does the final post-Q2000 system make better next-step decisions and preserve repaired knowledge over time?** That should be answered with targeted natural follow-up evidence, not another broad artificial beta.
