# Repair Supply Phase 2 — Priority B existing weak-pair review v0.1

Date: 2026-09-02
Decision: **do not upgrade either reviewed pair to formal STRONG.**

Production Repair Supply diagnostics identified Priority B Nodes where a different-Q candidate already exists but is currently classified `different_question_weak`. Before creating new questions, the existing pairs were manually reviewed for genuine independence.

## KN1256 — sagittal line of gravity

Active wrong: Q1272
Candidate: Q1457 (raw Node KN1432, canonicalized into KN1256)

Both questions are essentially the same fact-recall demand:

- Q1272 asks where the sagittal line of gravity passes and keys `外果前方`.
- Q1457 asks where the quiet-standing line of gravity passes and also keys `外果前方`.
- both are `fact_recall / KNOW`, level 1;
- both expose almost the same landmark statement and answer cue.

**Decision: remain WEAK.** A reviewed STRONG-pair override would overstate independence and could let memorization of the same wording count as repair confirmation.

Needed supply: create a third question that applies the line-of-gravity position to a different biomechanical interpretation or measurement demand.

## KN0725 — extraocular muscles and cranial-nerve innervation

Active wrong: Q733
Candidate: Q949 (raw Node KN0940, canonicalized into KN0725)

The pair is somewhat broader than KN1256 but still materially overlaps:

- Q733 directly asks which extraocular muscle is not innervated by the oculomotor nerve; correct answer is superior oblique / trochlear nerve.
- Q949 is a two-answer muscle-nerve matching item whose correct set explicitly contains `上斜筋―滑車神経` plus `上眼瞼挙筋―動眼神経`.
- both are `fact_recall / KNOW`, level 1;
- the exact fact that repairs Q733 is directly repeated as one of Q949's keyed choices.

**Decision: remain WEAK.** Q949 adds another fact but does not provide sufficiently independent evidence that the learner can use the innervation knowledge outside the same matching/recall format.

Needed supply: if this Node reaches the next creation batch, use a different demand such as lesion/finding interpretation rather than another muscle-nerve matching question.

## Policy consequence

No entry is added to `strong_different_question_pairs.json` for either pair.

Repair Supply Phase2 continues to prefer genuine new independent evidence over metadata overrides. A reviewed STRONG-pair override should be reserved for cases that are materially different despite identical coarse tags, not for near-duplicate recall questions.
