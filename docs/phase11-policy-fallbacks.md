# Phase 11 Policy Fallbacks

Date: 2026-09-01

When a higher-priority Phase 11 rule lacks enough evidence to choose safely, fall downward rather than inventing certainty.

Fallback principles:

- ambiguous ordinary wrong -> do not escalate to field repair; continue coverage/current guidance
- unresolved tie -> deterministic field_id fallback after evidence-based tie-breaks
- missing field evidence -> preserve current deterministic recommendation when possible
- no qualifying repair/recheck/coverage/stabilization -> maintenance adaptive30
- missing optional activity metadata -> judgment still works from formal attempts/field evidence
- missing selection audit -> do not infer selector consistency; mark it unavailable
- never use consultation text as a fallback signal
- never use question-bank prevalence as a learner weakness proxy
- never bypass Phase 10 Recent Cooldown from Phase 11

Every fallback should remain explicit in reason/evidence output so absence of evidence is visible rather than silently converted to confidence.
