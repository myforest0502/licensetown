# LicenseTown agent/development instructions

Before changing code, data, tests, workflows, or product behavior, read `docs/CURRENT_STATE.md`.

That file is the durable development source of truth for:
- what is already working,
- what is not finished,
- known problems/risks,
- the intended target state,
- next concrete work,
- important acceptance evidence.

Do **not** restart work by rediscovering the whole repository unless the status file is clearly stale or contradicted by the files being changed.

Whenever a meaningful change alters implementation status, validation status, design decisions, production behavior, data contracts, risks, or next work, update `docs/CURRENT_STATE.md` in the same development cycle.

Distinguish these levels explicitly:
1. code exists,
2. tests pass,
3. real data has been observed,
4. production behavior has been accepted.

Never mark a feature complete merely because code exists.

Project priority: practical improvement for the learner and national-exam success over architectural elegance. Prefer small changes followed by verification and real-use evidence.

Avoid casual changes to Production DB, Render, LINE behavior, or `main`. Work on the designated safe branch unless promotion criteria have been met.
