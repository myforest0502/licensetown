# LicenseTown agent/development instructions

## Cross-chat / new-session startup rule

Whenever a new chat, new agent session, Codex session, or resumed development thread is clearly about LicenseTown, **do not wait for the user to remind you of project state**.

Your first repository action must be to read `docs/CURRENT_STATE.md` from the current working branch (or the designated safe branch if already known). Use that file as the starting source of truth, then verify only facts that may have changed since its last update.

If the branch is unknown, first determine the active/designated working branch, then read that branch's `docs/CURRENT_STATE.md` before re-investigating architecture or status.

Do not ask the user to paste a handoff again merely because the chat room changed. The durable handoff is the repository state plus `docs/CURRENT_STATE.md`.

If `docs/CURRENT_STATE.md` is missing, stale, or contradicted by the code/data being touched, repair the document during that work cycle before proceeding broadly.

## Ongoing source-of-truth rule

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
