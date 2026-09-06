# Phase 11 Natural-use Session Load Evidence v0.2

Date: 2026-09-06
Status: observational evidence only / Shadow promotion boundary unchanged

## Why v0.2 exists

The first review correctly recorded 200 same-day answers and the fall in cumulative 50-question block accuracy, but later event-timing inspection shows that the 200 answers were not one uninterrupted sitting. This note tightens the interpretation boundary before any Phase11 policy uses same-day load evidence.

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

Production event timestamps show a major break between the morning set and the next study period. The morning study activity ended around 08:16 JST and the next major study set began around 13:38 JST, a gap of more than five hours.

Therefore the four 50-question blocks describe **same-day cumulative load**, not four consecutive blocks from one continuous 200-question sitting.

The late-day decline is compatible with fatigue or concentration decline, but it is also compatible with differences in question mix, target difficulty, route composition, time of day, and other session effects. Current evidence cannot identify the cause.

`phase11_session_load_facts.py` now exposes the study-day span and largest inter-attempt gaps so future review does not silently equate same-day volume with uninterrupted session duration.

## Repair signal from this study day

Same-day repeats were substantially more accurate than first exposures (86.5% vs 70.3%). This supports the limited conclusion that repeated work was not obviously ineffective on this day. It does not prove long-term retention, because same-day success can still reflect short-term memory.

Long-term repair effectiveness must still be judged by later formal transitions:

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
