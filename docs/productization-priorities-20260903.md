# LicenseTown post-core productization priorities — 2026-09-03

Status: agreed priority memo. This does not change runtime behavior.

## Positioning

The immediate priority remains completion of the current learning-engine core through items 9-12, with item 8 continuing as natural-use validation. After the core completion gates are met, the following four themes become the primary productization program.

These are not optional polish. They are required to turn LicenseTown from a working family-built learning system into a product that other learners/supporters can trust, understand, use, and pay for.

## 1. Make every learning route reliable

LicenseTown is not only "今日のおすすめ".

Required learning routes include at least:

- recommended study;
- field selection within the recommended flow where supported;
- learner-chosen field study;
- 熱血 mode;
- shared answer/scoring/explanation/continue flow;
- pause/resume and HOME return behavior.

A real-use report already showed that choosing a field outside the default recommendation could fall into repeated/incorrect replies. Treat this as a product-blocking reliability problem, not a minor UI issue.

Completion contract:

- exercise each route from entry -> question -> answer -> scoring -> explanation -> continuation -> finish/HOME;
- fix route/state collisions and repeated-response loops;
- run regression coverage across all routes after each fix;
- "recommended works" is not enough if learner-directed or 熱血 paths are broken.

## 2. Fully separate supporter view from developer diagnostics

Do not keep adding internal diagnostics to the supporter/parent screen.

The supporter question is intentionally simple:

> 「昨日あいつ、どこまでやったんだろう」

The supporter view should focus on:

- total questions completed;
- questions by field;
- learning time;
- understandable current ability/reach;
- whether progress toward the exam appears on track based on LT's evidence;
- whether the current learning pace/direction needs attention.

Internal concepts such as Node IDs, STRONG/WEAK evidence, Phase11, Baseline/Shadow, selection reasons, cooldown diagnostics, repair-supply internals, and detailed engine audits do not belong on the normal supporter screen.

Developer diagnostics should become a separate internal console with its own route/data loading boundary.

The developer console can grow over time to include:

- LT learning diagnostics;
- Question Bank audit;
- Knowledge Node state;
- Repair Supply;
- Phase11/Phase12 diagnostics;
- repeat/cooldown evidence;
- performance/latency diagnostics;
- DB/learning-history inspection;
- errors and product QA signals.

Goal: during development, opening the developer console should be enough to inspect LicenseTown without using the supporter UI as an engineering dashboard.

## 3. Make supporter monitoring intentionally lightweight and fast

This is more than hiding developer panels with CSS.

The supporter page should avoid performing unnecessary diagnostic queries/calculations in the first place.

Target design:

- load only the data needed for supporter questions;
- use plain-language summaries;
- avoid expensive internal diagnostic aggregation on normal page open;
- measure actual latency before/after changes;
- optimize the critical first-open experience.

Do not invent a hard latency target before measurement, but the acceptance review must include real timing for page open and the expensive sub-operations.

## 4. Commercialization and revenue become a formal workstream

A good product that cannot acquire paying users cannot fund continued development.

Revenue is an explicit requirement, not an embarrassing side effect. Sustainable income can fund:

- infrastructure and AI usage;
- performance improvements;
- design and outside expertise;
- marketing/customer acquisition;
- faster iteration;
- continued product development;
- the founder's own livelihood.

The workstream must cover the full path rather than treating the website as the goal:

`SNS / discovery -> official website -> LINE / onboarding -> first study -> continued use -> paid conversion -> retention`

Required productization questions:

- Who is the first paying customer: learner, parent/supporter, or both?
- What specific pain makes them pay?
- What is LicenseTown's one-sentence differentiated value?
- What proof creates trust?
- What is free vs paid?
- What price/model is justified by delivered value?
- What onboarding gets a new user to the first useful study session quickly?
- What signals predict dropout and what improves retention?
- Which channels can repeatedly bring qualified learners/supporters to the website?

Existing official-HP work should ultimately be judged as a conversion path, not merely a visual site.

## Execution priority after core completion

Current proposed order:

1. learning-route reliability;
2. supporter/developer separation architecture;
3. supporter lightweight/fast rebuild;
4. developer console expansion;
5. commercialization gap audit;
6. website / pricing / onboarding / SNS / conversion implementation and experiments.

Commercialization research/design can run in parallel when it does not disrupt core reliability work, but do not send traffic to a product whose main learning routes are still unreliable.

## Product standard

A sellable LicenseTown should increasingly satisfy five user-visible properties:

- fast;
- reliable;
- understandable;
- learner-directed when desired;
- trustworthy enough to delegate study direction to LT.

The learning engine can be sophisticated internally while the learner/supporter experience remains simple.

## Non-goals

- no decorative redesign without a user/business purpose;
- no developer diagnostics leaking into supporter UI merely because the data already exists;
- no pretending that follower counts or page views equal revenue;
- no sacrificing learning integrity for conversion metrics;
- no large marketing push before the core learning routes are dependable.