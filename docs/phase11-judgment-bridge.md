# LicenseTown ⑪ 判断システムへの橋渡し設計

Date: 2026-09-01
Status: design / shadow-only until promotion gate.

## 目的

⑪は単に「正答率が低い分野を出す」のではなく、受験生の現在地・弱点・修復状況・保持確認・直近行動をまとめて、今日の学習目的と範囲を判断する層とする。

⑩が「具体的なQの選び方」、⑪が「今日は何を目的に学ぶか」を決める。

## 責任分離

### ⑩ — exact question selection

Inputs include attempts, Node state, repair evidence, Safety and Recent Cooldown.

Outputs include question_id and selector audit metadata.

### ⑪ — intent/scope judgment

Inputs may include:

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
- user-facing explanation later, after promotion

## Initial intents

- repair
- recheck
- coverage
- stabilization
- maintenance

## Design rule

Choose field/purpose first, then let Phase 10 choose exact questions inside the permitted scope.

Do not let Phase 11 duplicate Recent Cooldown, strong/weak/same classification, or formal Node-state transitions.

## Recommendation activity

Recommendation plan/progress is context. Completion is based on formal answers in the target field, regardless of which route produced them.

An incomplete plan is not evidence of poor motivation or compliance.

## Selection audit use

Phase 10 audit can reveal contradictions after selection, for example:

- repair intent but almost no repair selections
- coverage intent with unnecessary recent bypasses
- unexplained concentration in one selection reason

Audit metadata is not direct mastery evidence and must not mutate Node state.

## Explanation policy

Internal reason codes should map to short learner-facing explanations only after promotion. Do not expose internal scores.

Examples:

- insufficient_coverage -> 実力を判断する問題数がまだ少ないため
- confident_wrong_cluster -> 自信を持って間違えた内容が重なっているため
- repeated_wrong_cluster -> 同じ知識領域でつまずきが続いているため
- recheck_due -> 一度できた内容が定着しているか確認するため
- uncertain_correct_cluster -> 正解できているが迷いが残っているため

## Privacy

Consultation usage may be an activity fact. Consultation text/content is never a judgment input.

## v0.1 exclusions

- no LLM decision authority
- no consultation-text analysis
- no pass-probability assertion
- no strong field weakness claim from one ordinary wrong
- no fixed demo values
- no exact Q IDs from the judgment layer
- no Node-state mutation

## Implementation order

1. deterministic decision table
2. pure read-only shadow module
3. diagnostics-only integration
4. current-vs-shadow comparison
5. natural-use review
6. separate explicit promotion change only if evidence supports it

Learner-facing recommendation must remain unchanged during initial shadow implementation.
