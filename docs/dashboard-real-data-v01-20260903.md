# Dashboard real-data derivation v0.1 — 2026-09-03

Status: design only. No learner-facing switch in this change.

## Goal

Replace remaining demo/legacy dashboard interpretations with deterministic values derived from the canonical Question Bank plus persisted learner evidence.

Target dashboard functions:

1. overall reach / progress;
2. field reach / progress;
3. weakness TOP3;
4. field-specific advice inputs;
5. recommended-question inputs.

The implementation should reuse the existing `field_evidence` / `field_progress` / Phase11 evidence pipeline rather than create another independent scoring model.

## Design principle

A dashboard number should answer a clear learner question.

- Coverage: “How much of the syllabus have I actually touched?”
- Mastery/state: “Of what I have touched, how stable is it?”
- Progress: “How far through the total canonical syllabus am I, accounting for learning state?”
- Weakness: “Where is there enough evidence that I should repair something?”
- Recommendation: “What should I do next?”

Do not present raw accuracy alone as mastery.

## Existing state scores

Reuse the current `field_progress.py` state scoring contract unless a later evidence review changes it:

- unseen = 0.00
- repairing = 0.10
- checking = 0.30
- recheck_due = 0.60
- repaired = 0.70
- stable = 1.00

The current identity remains:

`progress = coverage × touched-state mastery`

No confidence multiplier, retention multiplier, repeated-weakness adjustment, or written-evidence adjustment should be silently added in v0.1.

## Overall progress

Primary future dashboard value:

`overall_progress_percent = sum(canonical Node state scores) / total unique canonical Nodes × 100`

This should eventually replace the legacy activity-volume formula as the learner-facing “総合到達度”.

Keep the legacy value available internally during the shadow comparison period so regressions can be inspected, but do not average the two values together.

Required supporting display data:

- total canonical Nodes;
- touched canonical Nodes;
- unseen count;
- checking count;
- repairing count;
- repaired count;
- recheck_due count;
- stable count.

## Field progress

For each of the 18 formal fields, derive:

- canonical Node count;
- touched Node count;
- Node coverage percent;
- touched-state mastery percent;
- field progress percent;
- question count / accuracy as supporting context only.

Multi-field canonical Nodes must follow the existing canonical membership contract. Do not duplicate a Node in the overall denominator.

## Weakness TOP3

Weakness ranking must be based on actionable evidence, not simply the three lowest percentages.

Candidate evidence in priority order:

1. Critical Safety weakness;
2. confident-wrong / repeated wrong evidence;
3. active repairing Nodes with evaluable evidence;
4. recheck_due Nodes that need retention confirmation;
5. materially low field progress with sufficient attempts;
6. insufficient coverage only when stronger weakness evidence is absent.

Guardrails:

- one ordinary wrong answer must not dominate a field recommendation;
- low sample-size fields should be labeled “coverage insufficient,” not “weak”;
- unanswered fields should not occupy all TOP3 positions;
- a field with high accuracy but tiny coverage can still be a coverage priority, but that is not the same as a weakness;
- Safety must be able to outrank ordinary coverage/accuracy signals.

The dashboard should distinguish `weakness_reason` from `coverage_reason`.

## Field advice

Advice should be deterministic from evidence categories in v0.1. Do not call OpenAI on every dashboard render.

Suggested advice intents:

- `safety_repair`
- `confident_wrong_repair`
- `repeated_wrong_repair`
- `repairing_continue`
- `retention_recheck`
- `coverage_expand`
- `stable_maintain`

Each intent can map to short fixed copy. AI may later add conversational wording, but the underlying reason must remain stored/inspectable.

## Recommended-question inputs

The dashboard itself should not invent a second question selector.

It should produce a recommendation request/intent for the existing learning-strategy / adaptive selector path, including:

- target field(s);
- target canonical Node(s) when evidence supports Node-level repair;
- intent: repair / checking / exploration / maintenance;
- priority reason;
- Safety priority;
- new vs review preference;
- requested question count.

The exact Q IDs should continue to be chosen by the formal selector with Recent Question Cooldown and repair-evidence rules intact.

## Relationship to Phase11

Until Phase11 is promoted from Shadow-only, learner-facing “next study” should not silently switch to Phase11 just because the dashboard uses better progress metrics.

Dashboard progress modernization and Phase11 recommendation promotion are separate changes.

Allowed during shadow phase:

- calculate the new progress metrics;
- compare legacy and new values;
- show preview behind existing flags;
- log deterministic recommendation evidence for diagnostics.

Not allowed without a separate promotion decision:

- replacing current recommendation policy with Shadow output;
- changing Phase10 exact-Q selection semantics;
- changing Node-state transitions.

## Data sources

Canonical/static:

- Question Bank JSON;
- question tags;
- Knowledge Node canonical mapping.

Learner evidence:

- `question_attempts` as normalized durable attempt history;
- `user_node_state` as rebuildable derived state;
- `learning_events.question_results` only for event/audit metadata where needed;
- learning-time tables only for activity/supporting display, not mastery.

No new DB table is required for v0.1 calculation.

## Computation boundaries

Prefer pure functions for evidence -> metric transformations.

Suggested layers:

1. DB read functions return raw learner evidence;
2. evidence builder canonicalizes attempts/Nodes;
3. progress calculator produces numeric metrics;
4. weakness/recommendation evidence builder produces reasoned candidates;
5. presentation layer converts values/reasons to UI-friendly copy.

Do not mix SQL, ranking, and presentation wording in one function.

## Shadow validation before learner-facing promotion

Collect at least these comparisons on real learner history:

- legacy overall progress vs Node-state overall progress;
- legacy weak fields vs evidence-ranked TOP3;
- current recommendation vs evidence-derived recommended intent;
- fields with small sample size;
- high-accuracy / low-coverage cases;
- confident-wrong cases;
- Safety cases;
- repaired / recheck_due / stable cases once they occur.

Promotion requires that differences are explainable and useful, not merely numerically different.

## Acceptance criteria for implementation

- No demo field values remain in the real-data path.
- Overall denominator uses unique canonical Nodes.
- All 18 fields are represented deterministically.
- Weakness TOP3 does not classify low-sample coverage as proven weakness.
- Safety can outrank ordinary weakness.
- Recommendations expose a reason/intent rather than only a field name.
- Existing adaptive selector / cooldown rules are not bypassed.
- No per-render OpenAI dependency.
- No new Production DB migration is necessary for v0.1.
- Pure calculation tests cover empty history, sparse history, mixed states, Safety, confident-wrong, recheck_due, and stable cases.

## Implementation sequence after Repair Supply

1. freeze the final Q1-Q1737 Question Bank audit baseline;
2. add/extend pure dashboard evidence tests;
3. build real-data weakness/recommendation evidence in shadow mode;
4. compare on Production-shaped history through diagnostics;
5. enable field/overall progress preview if not already enabled;
6. review actual learner/supporter usability;
7. only then replace legacy learner-facing values.

## Non-goals

- no Phase11 promotion;
- no scoring-weight tuning from one learner case;
- no new Question Bank DB table;
- no AI-generated dashboard facts;
- no Production migration in the design phase.