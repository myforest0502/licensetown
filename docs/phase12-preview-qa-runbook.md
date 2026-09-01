# Phase 12 Preview QA Runbook

Date: 2026-09-01
Status: implementation merged to main; visual QA pending with preview flag enabled.

## Current implementation

Main contains Phase 12 v0.1 Preview behind:

`ENABLE_PHASE12_GUIDANCE_PREVIEW`

Default is OFF.

When OFF, the learner-facing dashboard remains on the existing recommendation path.

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
