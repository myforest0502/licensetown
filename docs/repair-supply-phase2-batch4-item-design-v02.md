# Repair Supply Phase 2 — batch4 item design v0.2

Status: manual medical/content review candidate; not yet Question Bank data.

Targets: next five Priority C repairing Nodes from Production repair-supply evidence after batch3. Proposed IDs assume main ends at Q1620; Codex must reconfirm before writing.

Design rule: same canonical Knowledge Node, materially different demand from the active-wrong source. Structural `different_question_strong` is necessary but not sufficient; stems and distractors must remain educationally independent.

## Q1621 — KN1395
- Active wrong: Q1420
- Existing concept: one motor unit = one alpha motor neuron plus all muscle fibers it innervates; fibers of one motor unit are activated together.
- New demand: `finding_interpretation / INTERPRET`
- Stem: Assume that only the axon of one alpha motor neuron is selectively injured. Which muscle fibers would directly lose neural input from that lesion?
- Choices:
  A. All fibers in the entire muscle
  B. Only the single fiber nearest the motor end plate
  C. All muscle fibers belonging to that motor unit
  D. Only type I fibers in the muscle
  E. Only fibers innervated by neighboring motor neurons
- Correct: C
- Rationale: a motor unit comprises one alpha motor neuron and all skeletal muscle fibers innervated by its axon. Injury to that motor neuron/axon denervates the fibers belonging to that motor unit, not every fiber in the whole muscle.
- Tag target: KN1395, task=finding_interpretation, primary_ability=INTERPRET, secondary_ability=KNOW, level=3, safety=none, source=original.

## Q1622 — KN0678
- Active wrong: Q686
- Existing concept: in later adulthood, judgment based on accumulated experience/knowledge is relatively preserved while encoding and processing speed may decline.
- New demand: `finding_interpretation / INTERPRET`
- Stem: A healthy older adult gives accurate answers to vocabulary and familiar practical-judgment questions but needs more time to learn a novel symbol-digit task and recalls fewer newly presented items after a delay. Which interpretation best fits normal late-adulthood cognitive change?
- Choices:
  A. Accumulated knowledge and experience-based judgment may remain relatively preserved while processing speed and new learning/encoding decline.
  B. All cognitive abilities should decline at the same rate.
  C. Preserved vocabulary excludes any age-related cognitive change.
  D. Slower processing alone proves dementia.
  E. New learning improves while crystallized knowledge is preferentially lost.
- Correct: A
- Rationale: normal aging is heterogeneous, but crystallized knowledge and experience-based judgment are often relatively preserved compared with processing speed and some aspects of encoding/new learning. The pattern alone does not diagnose dementia.
- Tag target: KN0678, task=finding_interpretation, primary_ability=INTERPRET, secondary_ability=KNOW, level=3, safety=none, source=original.

## Q1623 — KN0002
- Active wrong: Q2
- Existing concept: dynamic knee valgus is associated with inadequate control of hip abduction/external rotation, especially during single-leg tasks.
- New demand: `intervention_selection / PRESCRIBE`
- Stem: During a single-leg squat, the pelvis drops contralaterally and the femur moves into adduction/internal rotation, producing dynamic knee valgus. No acute ligament injury is suspected. Which exercise strategy most directly addresses the observed proximal control deficit?
- Choices:
  A. Strengthen and retrain hip abductors/external rotators with single-leg movement-control practice.
  B. Train only ankle plantar-flexor maximal strength.
  C. Avoid all hip exercise and strengthen knee extensors in open chain only.
  D. Stretch the hip external rotators aggressively before every repetition.
  E. Immobilize the knee in full extension during gait training.
- Correct: A
- Rationale: femoral adduction/internal rotation and pelvic drop during a single-leg task point to deficient proximal hip control. Hip abductor/external-rotator strengthening plus neuromuscular movement retraining directly targets the mechanism contributing to dynamic valgus.
- Tag target: KN0002, task=intervention_selection, primary_ability=PRESCRIBE, secondary_ability=INTERPRET, level=3, safety=none, source=original.

## Q1624 — KN1468
- Active wrong: Q1493
- Existing concept: psychotherapy is not intended to create positive transference; in psychodynamic therapy, transference is understood/interpreted to work with underlying conflict and relationship patterns.
- New demand: `intervention_selection / PRESCRIBE`
- Stem: In psychodynamic psychotherapy, a patient begins idealizing the therapist and repeatedly says, "Only you can understand me; I should make every important decision based on what you say." What is the most appropriate therapeutic handling of this transference?
- Choices:
  A. Encourage the idealization because positive transference is the treatment goal.
  B. Explore and interpret how the patient's feelings toward the therapist may reflect recurring relationship patterns and conflicts.
  C. Accept responsibility for making the patient's major life decisions.
  D. End therapy immediately because any transference indicates treatment failure.
  E. Ignore the relationship material and discuss symptoms only.
- Correct: B
- Rationale: transference can be therapeutically examined rather than deliberately produced as an endpoint. Psychodynamic work uses the therapeutic relationship to understand recurring patterns, defenses, and conflicts while maintaining appropriate boundaries.
- Tag target: KN1468, task=intervention_selection, primary_ability=PRESCRIBE, secondary_ability=INTERPRET, level=3, safety=none, source=original.

## Q1625 — KN0065
- Active wrong: Q65
- Existing concept: support should combine physical activity with social participation rather than addressing either in isolation.
- New demand: `intervention_selection / PRESCRIBE`
- Stem: A community-dwelling older adult has become physically inactive after retirement and also stopped attending neighborhood activities. There is no acute medical contraindication to exercise. Which plan best addresses both reduced physical activity and reduced social participation?
- Choices:
  A. Prescribe solitary bed exercises only and advise avoiding community activities.
  B. Recommend a graded walking/exercise program linked with participation in a suitable community group or activity the person values.
  C. Encourage social attendance but explicitly avoid any increase in physical activity.
  D. Focus only on passive range-of-motion exercise performed by a caregiver.
  E. Delay both activity and social participation until physical capacity returns spontaneously.
- Correct: B
- Rationale: the target problem includes both inactivity and loss of social participation. A graded, safe physical-activity plan integrated with meaningful community participation addresses both domains and supports sustained behavior better than isolated exercise or social advice alone.
- Tag target: KN0065, task=intervention_selection, primary_ability=PRESCRIBE, secondary_ability=DECIDE, level=3, safety=none, source=original.

## Implementation gate
- Codex must inspect Q1420/Q686/Q2/Q1493/Q65 and preserve the existing canonical Node IDs and category mapping.
- No reviewed STRONG-pair override may be added merely to force classification.
- Each new Q must classify `different_question_strong` versus its active-wrong source.
- Q1-Q1620 canonical question/answer/explanation/tag content must remain unchanged apart from array extension and required registry/head metadata.
- Full focused QA, full pytest, and Question Bank validator are mandatory before manual review.
