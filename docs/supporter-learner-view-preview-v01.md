# Supporter Learner View Preview v0.1

Date: 2026-09-01
Status: specification fixed / implementation pending

## Purpose

Allow an authorized supporter to inspect the learner-facing `合格への道` presentation at any time, even when the learner is unavailable, without granting the supporter the ability to act as the learner or mutate learner state.

This exists primarily for development/QA and support verification.

## Current problem

The supporter page currently contains a link labeled `本人の合格への道を見る`, but the destination is a read-only supporter rendering. This is useful for monitoring, but it is not the same presentation mode as the learner-facing route and can cause confusion during QA.

## Required behavior

Add a distinct supporter-only route and link labeled clearly as:

`本人画面プレビュー`

The preview must:

- require the existing signed supporter token
- require the supporter/learner active relationship via `authorized_supporter_learner()`
- render the same learner dashboard layout and learner-only visual elements
- use the learner's real stored dashboard data
- show learner-only buttons/controls in their normal positions for layout verification
- make every learner action inert in this preview
- perform no learner write, no recommendation-plan activity write, no learning start, no LINE send, no Node-state mutation
- never mint or expose a real learner dashboard token to the supporter
- never let the supporter impersonate the learner

The existing supporter read-only route must remain unchanged.

## Route

Suggested route:

`/supporter/goukaku-no-michi/learner-preview`

It should call `authorized_supporter_learner()` exactly as the existing supporter routes do.

## Template contract

Use the same `templates/goukaku/home.html` rather than duplicating the learner page.

Introduce a separate rendering concept from `read_only`:

- `read_only=True`: existing supporter read-only mode
- `learner_preview=True`: learner visual mode, but all interactions disabled
- normal learner route: both false

The preview should visually resemble the real learner page as closely as practical.

For learner-preview only:

- render buttons/cards that exist in learner mode
- remove live action data attributes / POST targets / usable hrefs, or replace with inert equivalents
- add one small unmistakable banner near the top: `本人画面プレビュー（操作はできません）`
- preserve layout dimensions/classes so QA remains representative

## Security and mutation rules

The preview route must not:

- call `record_activity_event()`
- create a learner dashboard token
- call the dashboard recommendation start endpoint
- send LINE messages
- write to DB
- alter attempts, sessions, Node state, or recommendations

The only allowed data access is the same read-side learner dashboard/supporter data already authorized by supporter linkage.

## Supporter page links

Keep the current read-only link, but rename it to avoid ambiguity:

`見守り用 合格への道` — `閲覧専用`

Add a new link immediately below:

`本人画面プレビュー` — `表示確認用・操作不可`

## Minimum tests

1. authorized supporter can open learner preview
2. unauthorized supporter receives 403
3. wrong learner ID receives 403
4. preview uses learner dashboard data
5. preview contains learner-only visual controls/cards
6. preview contains `本人画面プレビュー（操作はできません）`
7. preview contains no usable learner dashboard token
8. preview contains no live `data-recommendation-start-url`
9. preview contains no live `data-line-message`
10. preview does not call `record_activity_event()`
11. existing normal learner route behavior unchanged
12. existing supporter read-only route behavior unchanged
13. existing supporter page shows both clearly differentiated links
14. no DB migration
15. full pytest and relevant focused tests pass

## Completion

Complete when the supporter can independently verify the learner-facing layout at any time without needing the learner's device and without acquiring learner action privileges.
