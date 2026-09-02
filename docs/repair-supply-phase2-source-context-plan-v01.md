# Repair Supply Phase 2 — source context extraction plan v0.1

Before authoring Q1606+ content, extract only the ten active-wrong source records needed for the first five Priority A Nodes:

Q195, Q1599, Q684, Q1602, Q25, Q1596, Q331, Q1600, Q705, Q1603.

For each Q, capture from the current main Question Bank:

- stem and choices
- accepted/display answer
- explanation and per-choice explanations
- full question tag record
- canonical Node ID
- `(task, primary_ability)` demand pair

Also capture any reviewed strong-pair entries touching these Qs.

The extraction is diagnostic-only and must not modify Question Bank data. Temporary extraction scripts/workflows must be removed before any implementation PR is opened.
