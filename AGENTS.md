# LicenseTown agent/development instructions

## Cross-chat / new-session startup rule

Whenever a new chat, new agent session, Codex session, or resumed development thread is clearly about LicenseTown, **do not wait for the user to remind you of project state**.

Your first repository actions must be:
1. read `docs/CURRENT_STATE.md` from the current working branch (or the designated safe branch if already known),
2. read `docs/PT_V1_PRODUCT_GOAL.md`,
3. use both as the starting source of truth, then verify only facts that may have changed since their last update.

If the branch is unknown, first determine the active/designated working branch, then read those files before re-investigating architecture or status.

Do not ask the user to paste a handoff again merely because the chat room changed. The durable handoff is the repository state plus `docs/CURRENT_STATE.md` plus the fixed PT v1 product goal.

If `docs/CURRENT_STATE.md` is missing, stale, or contradicted by the code/data being touched, repair the document during that work cycle before proceeding broadly.

## PT v1.0 completion contract

`docs/PT_V1_PRODUCT_GOAL.md` is the durable shared definition of **「修正は今後もあるが、一旦完成として商品として出せる物」**.

Until Boss explicitly changes that definition:
- do not expand the v1.0 finish line merely because another improvement is possible;
- do not add speculative safeguards based only on "maybe someday" risk;
- classify new findings as either **v1.0 product blocker** or **v1.1+/backlog**;
- current priority is the main learner line: run, steer, stop, remain coherent, diagnose failures, and repair them;
- core learner loop is `wrong -> observable wrong-pattern analysis -> same-Node/different-Q repair -> repair confirmation -> day3 -> day7 -> one-month -> durable OR back to repairing`;
- product completion requires real learner usability and absence of serious study-blocking defects, not perfection or completion of every future feature.

Do not silently replace this goal with a broader engineering-quality goal.

## Ongoing source-of-truth rule

Before changing code, data, tests, workflows, or product behavior, read `docs/CURRENT_STATE.md` and ensure the change is compatible with `docs/PT_V1_PRODUCT_GOAL.md`.

`docs/CURRENT_STATE.md` is the durable development source of truth for:
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
