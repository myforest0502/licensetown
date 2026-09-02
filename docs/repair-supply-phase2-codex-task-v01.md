# Repair Supply Phase 2 — Codex task v0.1

This document is the implementation handoff after source-context extraction and item design are complete.

## Scope

Implement only the first five Priority A repair-supply questions defined in `docs/repair-supply-phase2-first-batch-v01.md`.

Expected new IDs at the current bank head: Q1606–Q1610, one question each for KN0194, KN0676, KN0025, KN0329, KN0697. Reconfirm the actual next sequential IDs before writing; never overwrite an existing Q.

## Files expected to change

At minimum:

- `data/question_bank/questions.json`
- `data/question_bank/answers.json`
- `data/question_bank/explanations.json`
- `data/question_bank/question_tags.json`
- derived/audit files only when the repo's existing scripts require regeneration
- focused tests for repair strength and bank integrity

Do not change selector weights, Phase11 ranking, Node state rules, DB schema/write logic, supporter/learner recommendation behavior, or historical Q1–Q1605 content.

## Required pre-write inspection

For each target Node, inspect both active wrong questions in all four Question Bank stores plus their tags. Record the existing `(task, primary_ability)` pairs and design the new item so its demand differs from both whenever clinically appropriate.

## Required validation

For every new Q:

- intended canonical Node exactly matches the target Node;
- keyed answer medically correct;
- distractors clinically plausible and discriminative;
- independent scenario/wording from both source questions;
- `classify_repair_confirmation(old_q, new_q) == different_question_strong` for both active wrong Qs where possible;
- if not possible by tag-demand diversity, stop and document the exact reason before adding a reviewed pair override;
- validator PASS;
- focused tests PASS;
- full pytest PASS (only the known unmanaged UTF fixture may be explicitly deselected if still present).

## Merge policy

Do not merge to main until manual medical/content review of all five new items is complete. Keep the implementation on a feature branch and provide a concise audit table with: new Q, Node, source Qs, new task/ability, answer, STRONG-vs-source results, distractor-quality note, independence note, and test results.
