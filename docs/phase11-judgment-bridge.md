# LicenseTown ⑪ 判断システムへの橋渡し設計

Date: 2026-09-02
Status: architecture implemented / Shadow diagnostics active / learner-facing promotion pending

## 目的

⑪は単に「正答率が低い分野を出す」のではなく、受験生の現在地・弱点・修復状況・保持確認・直近行動をまとめて、今日の学習目的と範囲を判断する層とする。

⑩が「具体的なQの選び方」、⑪が「今日は何を目的に学ぶか」を決める。

## 責任分離

### ⑩ — exact question selection

Inputs include attempts, Node state, repair evidence, Safety and Recent Cooldown.

Outputs include question_id and selector audit metadata.

### ⑪ — intent/scope judgment

Inputs include approved formal evidence such as:

- field coverage/accuracy evidence
- Node-state distribution
- confident/repeated wrong evidence
- recheck_due evidence
- uncertain-correct evidence
- recent learning volume/context
- recommendation plan/progress
- Phase 10 audit for post-selection consistency

Outputs:

- learning_intent
- target_field
- question_count
- recommended_route
- reason_code
- rationale evidence

## Implemented intents

- repair
- recheck
- coverage
- stabilization
- maintenance

## Architectural rule

Choose field/purpose first, then let Phase 10 choose exact questions inside the permitted scope.

Phase 11 does not duplicate Recent Cooldown, strong/weak/same repair classification, or formal Node-state transitions.

## Recommendation activity

Recommendation plan/progress is context. Completion is based on formal answers in the target field, regardless of which route produced them.

An incomplete plan is not evidence of poor motivation or compliance.

Persisted daily `recommendation_plan` activity is also suitable as a read-only historical Baseline anchor for retrospective Shadow QA. Historical replay must use only attempts available before that plan timestamp.

## Selection audit use

Phase 10 audit can reveal contradictions after selection, for example:

- repair intent but almost no repair selections
- coverage intent with unnecessary recent bypasses
- unexplained concentration in one selection reason

Audit metadata is not direct mastery evidence and must not mutate Node state.

## Explanation policy

Internal reason codes map to short learner-friendly wording in the Phase 12 preview, but the Shadow recommendation is not yet authoritative.

Examples:

- insufficient_coverage -> 実力を判断する問題数がまだ少ないため
- confident_wrong_cluster -> 自信を持って間違えた内容が重なっているため
- repeated_wrong_cluster -> 同じ知識領域でつまずきが続いているため
- recheck_due -> 一度できた内容が定着しているか確認するため
- uncertain_correct_cluster -> 正解できているが迷いが残っているため

Do not expose internal priority scores or developer comparison labels to the learner.

## Privacy

Consultation usage may be an activity fact. Consultation text/content is never a judgment input.

## v0.1 exclusions

- no LLM decision authority
- no consultation-text analysis
- no pass-probability assertion
- no strong field weakness claim from one ordinary wrong
- no fixed demo values as learner evidence
- no exact Q IDs from the judgment layer
- no Node-state mutation

## Implementation state

Completed:

1. deterministic J1→J7 decision table
2. pure read-only Shadow module
3. supporter diagnostics integration
4. current-vs-Shadow comparison
5. symmetric formal evidence profiles allowing either Current or Shadow to be stronger
6. Phase 12 additive preview presentation
7. supporting diagnostics for adaptive audit, repairability, repair-supply priority and repeat structure

Pending before learner-facing authority:

1. retrospective historical replay implementation
2. continuing natural-use review
3. review of Safety misses / single-wrong overreaction / sparse coverage / recheck_due handling
4. Phase 11 intent vs Phase 10 exact-selection consistency
5. explicit limited-pilot promotion decision only if evidence supports it

Learner-facing Baseline recommendation remains authoritative until that separate promotion decision.
