# Phase 11 Natural-use Session Load Evidence v0.1

Date: 2026-09-06
Status: observational evidence only / Shadow promotion boundary unchanged

## Scope

This note records one natural Production study day for the learner used in current real-use validation. It does not change Phase 11 J1-J7 ordering, Phase 10 exact-question selection, Recent Cooldown, Safety priority, Node-state semantics, or learner-facing recommendations.

## Observed same-day study

- study answers: 200
- correct: 149
- accuracy: 74.5%
- unique questions: 148
- repeat attempts: 52
- unique canonical Nodes observed: 143
- first exposures: 148 answers / 104 correct / 70.3%
- repeat attempts: 52 answers / 45 correct / 86.5%

Chronological 50-question blocks:

- attempts 1-50: 39/50 = 78.0%
- attempts 51-100: 39/50 = 78.0%
- attempts 101-150: 37/50 = 74.0%
- attempts 151-200: 34/50 = 68.0%

The final full block was 10.0 percentage points below the first full block.

## Route evidence

Observed route mix:

- manual: 95 attempts / 70.5%
- adaptive_daily: 90 attempts / 76.7%
- dashboard_recommendation: 10 attempts / 90.0%
- random: 5 attempts / 80.0%

The 90 adaptive_daily attempts preserved the current Phase 10 soft composition across three 30-question sets:

- repair: 45 total (40 repairing, 3 confident_wrong, 2 safety_wrong)
- checking: 30
- exploration: 15

Observed adaptive accuracies were 72.5% for repairing, 90.0% for checking, 60.0% for exploration, 100.0% for confident_wrong, and 50.0% for safety_wrong. These are descriptive outcomes from one day, not ranking weights.

## Interpretation boundary

The evidence supports two observations:

1. Same-day repeats were materially more accurate than first exposures in this session (86.5% vs 70.3%), so repair activity was not obviously ineffective.
2. Accuracy declined across the latter half of a long study day, with 68.0% in the final 50. This is compatible with fatigue, concentration decline, changing question difficulty/mix, or other causes. The data alone does not identify the cause.

Therefore this evidence must not be converted directly into a learner-facing stop rule or an automatic reduction in question count. Phase 11 already records `high_same_day_volume` from 60 answers onward as an observation-only signal. The added `phase11_session_load_facts.py` keeps volume, repeat structure, block accuracy, and leading-to-trailing accuracy delta as facts without deciding what action to take.

## Promotion consequence

The 2026-09-02 Phase 11 HOLD decision remains in force. This natural-use day strengthens the evidence base for long-session behavior but does not satisfy the still-missing promotion classes by itself, especially naturally occurring J4 `recheck_due` handling and subsequent stable retention evidence.

No Production DB write or policy mutation is required by this evidence note.
