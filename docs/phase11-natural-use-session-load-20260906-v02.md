# Phase 11 Natural-use Session Load Evidence v0.2

Date: 2026-09-06
Status: observational evidence only / Shadow promotion boundary unchanged

## Why v0.2 exists

The first review correctly recorded 200 same-day answers and the fall in cumulative 50-question block accuracy, but later event-timing and prior-answer-state inspection show two important interpretation limits:

1. the 200 answers were not one uninterrupted sitting;
2. the high overall repeat accuracy was mostly driven by questions that had already been answered correctly, so it cannot be used as a repair-effectiveness metric by itself.

This note tightens those boundaries before any Phase11 policy uses same-day load evidence.

## Confirmed Production facts

- same-day answers: 200
- correct: 149
- accuracy: 74.5%
- unique questions: 148
- same-day repeat attempts: 52
- unique canonical Nodes observed: 143
- first exposures: 148 / 104 correct = 70.3%
- repeat attempts: 52 / 45 correct = 86.5%
- confidence 1: 112
- confidence 2: 87
- confidence 3: 1
- confident-wrong answers: 12

Cumulative same-day 50-question blocks:

- attempts 1-50: 39/50 = 78.0%
- attempts 51-100: 39/50 = 78.0%
- attempts 101-150: 37/50 = 74.0%
- attempts 151-200: 34/50 = 68.0%

The last full cumulative block was 10.0 percentage points below the first.

## Important timing correction

Production timestamps show a major break between the morning set and the next study period. The morning activity ended at approximately 08:16 JST and the next study period began at approximately 13:38 JST.

The measured gap is about 322 minutes (5 hours 22 minutes). Other large same-day gaps observed were about 21.9, 12.9, 11.1, and 10.2 minutes.

Therefore the four 50-question blocks describe **same-day cumulative load**, not four consecutive blocks from one continuous 200-question sitting.

The late-day decline is compatible with fatigue or concentration decline, but it is also compatible with differences in question mix, target difficulty, route composition, time of day, and other session effects. Current evidence cannot identify the cause.

`phase11_session_load_facts.py` now exposes the study-day span and largest inter-attempt gaps so future review does not silently equate same-day volume with uninterrupted session duration.

## Repeat-state correction

The overall repeat accuracy of 86.5% looks strong, but chronological prior-answer-state inspection changes its interpretation.

Among the 52 repeat attempts:

- previous wrong -> current correct: 6
- previous wrong -> current wrong: 5
- previous correct -> current correct: 39
- previous correct -> current wrong: 2

So only 11 of the 52 repeats immediately followed a wrong answer. Of those 11, 6 became correct and 5 remained wrong: **54.5% immediate wrong-to-correct accuracy**.

By contrast, 41 repeats followed a previously correct answer, and 39 of those remained correct.

Therefore **generic repeat accuracy must not be treated as repair effectiveness**. The 86.5% figure is mostly a maintenance/repetition signal in this study day, not direct evidence that weak material was repaired.

The Phase11 same-day helper now reports repeat transitions separately:

- repeat-after-wrong count
- wrong -> correct
- wrong -> wrong
- repeat-after-wrong accuracy
- repeat-after-correct count
- correct -> correct
- correct -> wrong

This makes future natural-use review less vulnerable to a misleading aggregate repeat percentage.

## Repair effectiveness still requires formal evidence

Immediate wrong-to-correct improvement is useful descriptive evidence, but it still does not prove durable repair. Long-term repair effectiveness must be judged by later formal transitions:

- repairing -> repaired
- repaired -> recheck_due
- recheck_due -> stable or back to repairing

## Natural J4 timing

A read-only check of the currently reviewed STRONG different-question pairs found one confirmed repair sequence for KN0394:

- wrong answer on Q1572: 2026-09-01
- confidence=1 correct STRONG alternate Q399: 2026-09-02 18:32 JST
- corresponding seven-day retention review time: approximately 2026-09-09 18:32 JST

This is a **candidate timing marker from the reviewed-pair subset**, not a claim that it is the earliest possible recheck_due Node across the entire current repair-supply catalog. No timestamps or learner data were modified to create this evidence.

## Policy consequence

No learner-facing stop rule, fatigue rule, question-count reduction, J1-J7 ordering change, Phase10 selector change, Safety change, Recent Cooldown change, Node-state mutation, or Production DB write is justified by this review.

Phase11 remains Shadow-only. The next decisive evidence remains naturally occurring retention behavior and additional natural Baseline-vs-Shadow comparison diversity.
