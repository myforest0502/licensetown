# Repair Supply Phase2 batch10 medical/content review v0.1

Review scope: Q1651-Q1655 design in `docs/repair-supply-phase2-batch10-item-design-v02.md`.

## Q1651 / KN0966 — acute myocardial infarction biomarkers
**PASS with explicit early-testing caveat.**

- The source Q976 correctly distinguishes creatinine from myocardial-injury markers.
- Q1651 changes the demand from source finding interpretation to selecting the appropriate blood marker in a suspected acute MI case.
- Cardiac troponin is an appropriate central marker for myocardial injury.
- The item deliberately avoids claiming that a single early negative troponin excludes acute MI. The explanation must preserve the serial/clinical-context caveat.
- Do not introduce obsolete timing trivia about AST/LD/CK-MB as the core tested fact.

## Q1652 / KN0988 — steppage gait / common peroneal neuropathy
**PASS.**

- Steppage gait is appropriately linked to foot drop from ankle dorsiflexor weakness.
- The vignette localizes a peripheral lesion with dorsiflexion and eversion weakness, preserved inversion/plantarflexion, and lateral-leg/dorsum-foot sensory loss.
- This pattern supports common peroneal neuropathy and reduces ambiguity with L5 radiculopathy or isolated deep peroneal neuropathy.
- No claim is made that common peroneal neuropathy is the only possible cause of steppage gait.

## Q1653 / KN1029 — disability acceptance / denial
**PASS for content, with data-quality note.**

- Under the five-stage model used by the existing Question Bank, denial follows shock.
- The scenario asks the learner to interpret denial from behavior rather than recall the ordinal position.
- The explanation must state that real psychological adaptation is not necessarily linear and varies across individuals.
- KN1029 and KN1151 appear semantically overlapping but are not currently canonicalized together. Batch10 must not merge them or mutate the canonical map; that should be audited separately.

## Q1654 / KN1470 — BDI-II
**PASS.**

- BDI-II is correctly treated as a self-administered/self-report questionnaire concerning depressive symptoms.
- The item correctly avoids treating BDI-II alone as a definitive diagnostic test for a depressive disorder.
- No cutoff score is required, preventing avoidable dependence on scoring conventions outside the source Node's central concept.

## Q1655 / KN1475 — MS vs CIDP / sensory impairment
**PASS.**

- Multiple sclerosis is a CNS demyelinating disease and may cause sensory symptoms.
- CIDP is a peripheral demyelinating neuropathy and commonly includes sensory symptoms with weakness and reduced/absent reflexes.
- The vignette adds peripheral nerve-conduction findings and hyporeflexia, making peripheral demyelinating neuropathy the best interpretation without falsely implying that sensory symptoms alone distinguish CIDP from MS.

## Formal-content conclusion
All five designs are suitable for implementation as materially different questions relative to their designated source questions. No classifier change, reviewed STRONG override, source-question rewrite, canonical-map mutation, or official-answer-contract change is medically or formally justified.

**Manual medical/content review: PASS for implementation.**
