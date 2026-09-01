# Safety Strong-Repair Pilot Content Audit v0.1

Date: 2026-09-02
Scope: Q1595-Q1605
Status: manual content-quality audit; no Question Bank mutation.

## Purpose

Q1595-Q1605 were added to create formal `different_question_strong` repair supply for existing Safety repairing Nodes.

This audit asks a stricter question than structural validation:

> If a learner answers the alternate question correctly with confidence=1, is that result sufficiently discriminative to support meaningful `repairing -> repaired` evidence?

Structural STRONG classification and educational discrimination are not the same thing.

## Audit rules

Each item is reviewed for:

- medical correctness
- one-best-answer clarity
- distractor plausibility
- whether the task requires understanding rather than obvious elimination
- likely usefulness as independent repair-confirmation evidence

Source-Q textual independence could not be fully re-reviewed in this pass because the current GitHub connector could not reliably retrieve individual records from the large historical `questions.json` file. Therefore independence is marked `REVIEW` unless already established structurally by the formal Node/tag audit.

No deployed Q ID is changed by this document.

## Summary

| New Q | Source Q | Content correctness | Distractors | Source independence | Repair-evidence usefulness | Main concern |
|---|---|---|---|---|---|---|
| Q1595 | Q8 | PASS | WEAK-MEDIUM | REVIEW | MEDIUM | Clinical decision is valid, but most wrong choices are plainly unsafe or insufficient. |
| Q1596 | Q25 | PASS | MEDIUM | REVIEW | MEDIUM | Classic cervical myelopathy pattern; several alternatives are easy to exclude from Babinski/hyperreflexia. |
| Q1597 | Q36 | PASS | WEAK | REVIEW | MEDIUM-LOW | External cue effect is almost directly stated by the stem; alternatives are mechanistically remote. |
| Q1598 | Q109 | PASS | MEDIUM | REVIEW | MEDIUM | Correct comparison is appropriate, but several alternatives do not assess dual-task gait at all. |
| Q1599 | Q195 | PASS | WEAK | REVIEW | LOW | Stem localizes the problem to the entrance step, making the location answer nearly explicit. |
| Q1600 | Q331 | PASS | WEAK | REVIEW | LOW | Several distractors are self-disqualifying or directly contradict contracture prevention. |
| Q1601 | Q379 | PASS | MEDIUM-HIGH | REVIEW | HIGH | Requires the specific controlled-oxygen target of SpO2 88-92%; medically meaningful distinction. |
| Q1602 | Q684 | PASS | WEAK | REVIEW | MEDIUM-LOW | Correct emergency response is appropriate, but alternatives are conspicuously unsafe. |
| Q1603 | Q705 | PASS | WEAK | REVIEW | LOW | Age-only, limb-length-only, or unmonitored maximal load are implausible; answer can be chosen by elimination. |
| Q1604 | Q1305 | PASS | WEAK-MEDIUM | REVIEW | MEDIUM-LOW | Core concept is valid, but knee/ankle distractors are anatomically impossible after transfemoral amputation. |
| Q1605 | Q1504 | PASS | MEDIUM | REVIEW | MEDIUM | Safe medication response is appropriate, but several alternatives are obviously unacceptable professional behavior. |

## Item notes

### Q1595 / KN0008 / source Q8

**Keyed answer:** perform exercise-tolerance assessment when symptoms and circulation have stabilized, represented by the dialysis-following day in the stem.

**Medical review:** PASS.

The safety principle is appropriate: symptomatic post-dialysis hypotension/orthostatic symptoms should preclude routine exercise-tolerance testing until the patient is clinically stable.

**Discrimination:** MEDIUM.

A, B and E are clearly unsafe. C is a somewhat better distractor because it tests whether the learner understands that calendar timing alone is insufficient. The item is useful, but a confident correct response is not especially difficult.

**Possible future improvement:** make at least two distractors represent clinically plausible timing choices under stable versus unstable conditions instead of obviously unsafe testing.

### Q1596 / KN0025 / source Q25

**Keyed answer:** cervical myelopathy / corticospinal tract involvement.

**Medical review:** PASS.

Upper-extremity dexterity impairment, gait disturbance, hyperreflexia and Babinski signs are coherent with cervical myelopathy.

**Discrimination:** MEDIUM.

The pattern is clinically meaningful, but Babinski positivity makes peripheral neuropathy, shoulder disease and primary myopathy relatively easy to eliminate.

**Possible future improvement:** use closer central-neurologic differentials rather than several non-central disorders.

### Q1597 / KN0036 / source Q36

**Keyed answer:** visual external cue facilitates release of freezing of gait.

**Medical review:** PASS.

**Discrimination:** MEDIUM-LOW.

The stem itself describes a classic external-cue response. Muscle strength, ROM and cerebellar ataxia alternatives are distant from the phenomenon.

**Possible future improvement:** compare visual cueing with other plausible Parkinson gait strategies or ask which treatment principle the response supports.

### Q1598 / KN0109 / source Q109

**Keyed answer:** compare single-task and dual-task gait under monitored fatigue/safety conditions.

**Medical review:** PASS.

**Discrimination:** MEDIUM.

The case appropriately links community difficulty, fatigue and dual task. B is a meaningful partial distractor because it deliberately misses the provoking condition. A and D are too remote; E is mainly an unsafe extreme.

**Possible future improvement:** add plausible alternatives such as cognitive-only dual-task testing, non-fatigued dual-task gait, or fatigue assessment without gait comparison.

### Q1599 / KN0194 / source Q195

**Keyed answer:** provide stable support near the entrance step.

**Medical review:** PASS.

**Discrimination:** LOW.

The stem says gait is stable indoors and instability occurs only at the entrance step while the patient reaches for the wall. The correct location is effectively localized in the question itself.

A confidence=1 correct response may demonstrate reading comprehension more than repaired knowledge of home modification.

**Possible future improvement:** keep the same Node but ask placement/side/timing of support using functional analysis, with multiple plausible home-modification choices.

### Q1600 / KN0329 / source Q331

**Keyed answer:** cervical extension stretches the shortening anterior neck tissues and opposes flexion contracture.

**Medical review:** PASS.

**Discrimination:** LOW.

B, D and E are near-direct contradictions of the therapeutic objective. C is also narrowly incorrect. The correct answer stands out strongly.

**Possible future improvement:** use distractors involving plausible scar-management rationales, competing positioning goals, or incorrect tissue-direction reasoning rather than obviously harmful objectives.

### Q1601 / KN0374 / source Q379

**Keyed answer:** titrate oxygen toward SpO2 88-92% and reassess.

**Medical review:** PASS.

**Discrimination:** HIGH relative to the other pilot items.

The learner must know the controlled oxygen target for a COPD exacerbation patient at risk of hypercapnic respiratory failure. Leaving oxygen unchanged, stopping it entirely, or aiming for 100% represent clinically relevant distinctions.

This item is the clearest example in the pilot where confidence=1 correct plausibly adds meaningful independent confirmation.

### Q1602 / KN0676 / source Q684

**Keyed answer:** stop training and obtain urgent circulatory assessment for suspected neurogenic shock.

**Medical review:** PASS.

Hypotension, bradycardia and warm skin after cervical SCI fit neurogenic shock.

**Discrimination:** MEDIUM-LOW.

The correct safety response is appropriate, but increasing exercise load, ignoring bradycardia, or cooling the skin are conspicuously poor choices.

**Possible future improvement:** compare urgent responses that are all superficially plausible, while preserving the rehabilitation-professional scope of action.

### Q1603 / KN0697 / source Q705

**Keyed answer:** evaluate exercise tolerance while monitoring symptoms and SpO2 to establish a safe starting intensity.

**Medical review:** PASS.

**Discrimination:** LOW.

Age only, resting heart rate only, limb length only, and unmonitored maximal loading make the correct answer obvious by general test-taking logic.

**Possible future improvement:** provide several plausible exercise-prescription methods and require selection of the method appropriate to severe COPD on home oxygen.

### Q1604 / KN1288 / source Q1305

**Keyed answer:** hip flexion contracture.

**Medical review:** PASS.

Prolonged wheelchair sitting and a pillow under the residual thigh maintain hip flexion and favor flexion contracture.

**Discrimination:** MEDIUM-LOW.

The concept is useful, but knee and ankle options are anatomically impossible on the amputated side after transfemoral amputation, removing two distractors immediately.

**Possible future improvement:** use plausible hip-position contractures, abduction/adduction contracture, lumbar compensation, or positioning consequences rather than absent joints.

### Q1605 / KN1479 / source Q1504

**Keyed answer:** explore symptoms/concerns and support consultation with the prescriber rather than abrupt self-discontinuation.

**Medical review:** PASS.

Abrupt benzodiazepine discontinuation can cause withdrawal, and medication adjustment belongs with the prescribing clinician.

**Discrimination:** MEDIUM.

The safe professional response is meaningful, although A, C, D and E are largely inappropriate professional behaviors.

**Possible future improvement:** use closer alternatives involving communication timing, fall-risk management and prescriber coordination rather than overtly dismissive or unsafe advice.

## Decision

### Medical validity

No keyed answer in Q1595-Q1605 was identified as clearly medically incorrect in this audit.

### Structural formal status

Do not change the existing `different_question_strong` structural classification solely from this audit. Structural demand difference and item discrimination are separate dimensions.

### Evidence-quality caution

Do **not** interpret a future rise in `repaired` Nodes from these 11 questions as sufficient proof that the strong-repair design is educationally calibrated.

Highest-priority content review before treating the pilot as high-quality repair evidence:

1. Q1600
2. Q1603
3. Q1599
4. Q1602
5. Q1604

Q1601 is the strongest current exemplar.

## Before any Question Bank edit

First determine whether each Q1595-Q1605 has already appeared in Production attempts.

If a question has been used, do not silently rewrite its educational meaning. Choose explicitly among:

- revise only when historical interpretation remains compatible
- retire the item from future repair confirmation while preserving history
- add a better replacement question

Any content change must preserve validator integrity and historical learner evidence.
