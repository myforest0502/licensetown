# Phase 12 Preview QA Runbook

Date: 2026-09-01
Status: implementation merged to main; PC and supporter visual QA observed; learner-owner mobile/action and final flag-OFF restoration still pending.

## Current implementation

Main contains Phase 12 v0.1 Preview behind:

`ENABLE_PHASE12_GUIDANCE_PREVIEW`

Default is OFF.

When OFF, the learner-facing dashboard remains on the existing recommendation path.

## QA progress recorded on 2026-09-01

Completed/static:

- Preview implementation is on main
- focused tests passed before merge
- full suite passes except the known unmanaged `questions_master_candidate_v2_q1_q100.json` fixture absence
- Question Bank validator passes at Q1-Q1594
- no DB migration / Production DB write / selector change / Node-state change
- feature flag is enabled for the explicit QA window
- PC screenshot confirms the Preview card renders without clipping or horizontal layout break
- headline/reason/six-state counters/attention row are readable on the observed PC surface
- observed state counts sum to 1509 Canonical Nodes
- no raw Knowledge Node ID, priority score, or developer comparison label is visible in the observed Preview card
- code inspection confirms the Preview reuses the existing `[data-recommendation-start-url]` JavaScript handler and existing recommendation POST path; no Phase 12-only learning API was added
- supporter read-only screenshot confirms `閲覧専用` remains visible
- supporter Preview renders without material clipping or overlap
- supporter Preview contains no learner start action, as designed
- existing supporter read-only layout remains intact on the observed surface

Still requires visual confirmation:

- learner-owner view action button presence and placement
- smartphone learner-owner layout
- Preview action displays the same field/count that it starts
- baseline restoration after flag OFF at the end of the QA window

## Purpose of visual QA

Visual QA checks presentation only. It does not decide whether Phase 11 should replace the current learner-facing recommendation.

The preview remains a pilot even if the UI looks correct.

## PC checks

With the flag ON and a valid learner token:

- `🧭 次にやること Preview` is visible
- headline is readable without clipping
- reason text wraps naturally
- six state counters are visible and aligned
- attention item content does not overflow
- current `今日のおすすめ学習` card is still present
- current recommendation is not silently replaced
- Preview action is visible only in learner view
- no raw Knowledge Node ID appears
- no priority score appears
- no developer comparison label appears
- existing overall/field progress layout is not broken
- existing footer/actions remain usable

## Mobile checks

At smartphone width:

- preview card fits without horizontal scrolling
- state summary collapses to 3 columns as designed
- attention item wraps without overlap
- Preview action is full width and tappable
- existing recommendation card remains readable
- no content is clipped at left/right edges
- long Japanese field names wrap safely

## Supporter checks

In supporter read-only view:

- Preview content may be displayed
- `閲覧専用` remains visible
- no Preview start button is present
- no existing read-only protections regress

## Behavior checks

Do not use the Preview card to approve Phase 11 promotion yet.

Verify only:

- button invokes an existing study route
- no new learning API exists solely for Phase 12
- ordinary current recommendation still functions
- turning the flag OFF removes the Preview and returns the exact baseline view

## Immediate fail conditions

Disable the flag if any of these occur:

- learner dashboard fails to render
- current recommendation disappears or changes unexpectedly
- wrong learner data is shown
- supporter view gains a learning action
- raw internal Node IDs or scores are exposed
- mobile layout becomes materially unusable
- Preview button launches a different question count/field than displayed

## Promotion remains blocked by evidence gate

Even after visual QA passes, Phase 12 does not replace current guidance until:

- Phase 10 natural-use audit persistence is confirmed
- unexplained Recent Cooldown overlap is absent
- Phase 11 has no critical Safety misses in natural comparison
- single ordinary wrong answers do not cause repeated overreaction
- recheck_due is not starved
- sparse learners get suitable coverage guidance
- natural-use comparison supports Phase 11 over the baseline

## Phase 12 completion rule

Implementation/static QA is complete after visual QA passes.

Learner-facing promotion is a separate gate. Until that gate passes, keep `ENABLE_PHASE12_GUIDANCE_PREVIEW` OFF in ordinary production use or enable it only for an explicit QA/pilot window.