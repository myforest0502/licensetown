# Phase 10 Static Audit Gaps

Date: 2026-09-01
Status: static QA note; no Render or Production DB required.

## Current snapshot gap

`data/question_bank/question_tags_audit.txt` currently describes only Q1-Q1564:

- records: 1564
- duplicates: 0
- missing: 0
- errors: 0

The formal Question Bank is now Q1-Q1594, so the committed audit snapshot is stale by 30 questions.

The three later import lots are already present in current `question_tags.json`, including Q1565 onward, but their aggregate task/ability/level/safety distributions have not yet been folded into the committed audit report.

## Why this matters

The stale report does not imply the current Question Bank is invalid. Recent validators have passed at 1594 questions. It means only that the human-readable distribution snapshot is not current enough to use for present-day totals or concentration analysis.

Do not use the Q1564 report as evidence for current Q1594 percentages.

## Refresh requirement

Regenerate the audit from the current formal files and verify:

- Q range Q1-Q1594
- records 1594
- no duplicates
- no missing IDs
- no schema/reference errors
- task distribution
- primary/secondary ability distribution
- level distribution
- safety distribution
- source distribution if the validator already exposes it cleanly

The refresh is observational. Do not retag questions merely to make category distributions look balanced.

## Follow-on static checks

After the refreshed snapshot exists, compute or inspect:

- Safety concentration by field
- fact_recall concentration by field/source
- level concentration by field/source
- singleton vs multi-question canonical Node distribution
- strong/weak different-Q availability
- recently imported Q1565-Q1594 contribution to those distributions

Any imbalance becomes a review candidate, not an automatic rewrite.

## Phase 11 relevance

Question-bank distribution describes available evidence supply; it is not learner weakness. Phase 11 must never infer that a learner is weak in a field simply because the bank contains many questions there.
