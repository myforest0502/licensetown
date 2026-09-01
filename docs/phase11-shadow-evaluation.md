# Phase 11 Shadow Evaluation Plan

Date: 2026-09-01
Status: diagnostics-only evaluation policy.

Phase 11 shadow exists to compare deterministic learning-intent judgments with the current recommendation without changing learner-facing behavior.

For every eligible snapshot, capture current target/reason and shadow intent/target/question_count/reason_code/confidence/evidence plus a comparison label.

Review labels:

- same_target_same_reason
- same_target_stronger_reason
- different_target_shadow_has_stronger_evidence
- different_target_current_has_stronger_evidence
- insufficient_evidence_to_judge

Prioritize review of disagreements, especially Safety, confident/repeated wrong, recheck_due, and uncertain-correct cases. Also sample agreements so evaluation is not biased toward wins.

Shadow evaluation must not write learning events, mutate Node state, alter learner recommendations, change adaptive selection, consume consultation text, or treat selector score as mastery.

Promotion requires natural-use evidence of no critical Safety misses, no repeated overreaction to single ordinary wrongs, appropriate sparse-learner coverage, non-starvation of recheck_due, consistency between Phase 11 intent and Phase 10 audit, and fewer obviously irrelevant recommendations than the baseline.

Natural learner sessions are preferred. Do not manufacture Production DB learning events solely to generate shadow examples.
