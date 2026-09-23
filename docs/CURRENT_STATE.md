# LicenseTown Current State

## 2026-09-24 公開HPの無料βモニター導線を明確化

- 凍結済みのPC/724pxデザイン原本は変更せず、公開レンダー境界でのみ「第62回 理学療法士国家試験を受験する方へ」と「無料βモニター 先着30名募集中」をヒーロー付近に追加した。
- 主CTAは「LINEで無料βを始める」に統一。PCはQRコードとボタンを併記し、モバイルはボタンを優先してQRを非表示にする。
- 支援案内は削除せず、無料βCTAの後に配置した。Question Bank件数表示とLINE導線URLは従来の正式値・動作を維持する。

## 2026-09-23 Production natural-use runtime audit repair

- Production dashboard reads exposed auxiliary `written_check` payloads to the formal question-result aggregators, causing repeated `unknown question_id: None/''` warnings. Formal aggregators now silently ignore auxiliary result dictionaries that do not declare a `question_id`; a declared empty or unknown formal Q ID still emits the existing warning.
- A stale incomplete Strategy soft-pilot session previously raised during `completion_context()` and could invalidate later trustworthy completion context. Incomplete/duplicate/inconsistent pilot groups now receive no completion credit but do not invalidate later completed pilot, web recommendation, or recommendation-plan evidence. If no trustworthy context remains, the existing fail-closed fallback is preserved.
- Strategy fallback logging now records only the exception class and a controlled non-personal reason. Phase11 remains HOLD/Shadow-only; Strategy remains soft pilot and never gains exact-Q authority.
- Validation: relevant tests **134 passed**; full suite **1550 passed / 6 skipped / 1 deselected / 141 subtests**; formal Question Bank validator **Q1-Q2743, all four files 2743, 0 schema/reference/duplicate issues**.
- Production data, DB schema/migrations, Render configuration, selector/Safety/repeat/cooldown behavior, and Q1-Q2743 content are unchanged. Production deployment and real-use acceptance are still pending.

## 2026-09-22 provisional_bulk reviewed-first selection preference — LIVE

- The Q2234-Q2743 source-context rewrite and formal-evidence boundary remain the primary remediation.
- Natural use showed provisional supply could dominate an ordinary day (135/170 attempts before
  the wording correction), so reviewed items now receive selection preference when they can satisfy
  the same learning need.
- `tag_status=provisional_bulk` stays eligible as shortage/depth supply; it is not deleted or
  hard-blocked.
- Adaptive selection applies a **250-point editorial penalty** for
  exploration/checking/maintenance and an **80-point penalty** for repair. The smaller repair
  penalty preserves different-Q repair supply when reviewed alternatives are insufficient.
- Safety, repair-evidence quality, Recent Cooldown/repeat protection, coverage and retention
  rules remain unchanged and authoritative.
- PR #410 full CI: **1547 passed / 6 skipped / 1 deselected / 141 subtests passed**.
- This is a runtime quality preference, not a claim that the 510 items are editorially complete.

## 2026-09-22 Q2234-Q2743 formal-evidence version boundary

- Q2234-Q2743 question stems were source-context corrected and became live after the
  Q2743 rewrite deploy completed on 2026-09-22.
- Raw historical attempts are preserved, but attempts on Q2234-Q2743 from before
  `2026-09-22T13:48:28Z` are excluded from **formal derived learning evidence**
  for the current wording.
- Short-term repeat protection may still use the raw attempt history so the learner
  is not immediately re-served recently seen Q IDs solely because the wording version
  changed.
- This boundary prevents pre-rewrite wording defects from manufacturing false weakness
  in current Knowledge Node / selector evidence.
- It does not delete history and does not alter attempts outside Q2234-Q2743.

## 2026-09-22 Q2743 provisional rewrite and formal-evidence boundary — LIVE

- Q2234-Q2743 were source-context reconstructed from their uniquely mapped Q1-Q2000 source
  questions after natural-use audit found context/direction defects.
- Corrected wording became live at **2026-09-22T13:48:28Z**.
- Attempts on Q2234-Q2743 before that boundary remain durable raw history but are excluded from
  current formal learning evidence.
- The primary learner had **135** such superseded attempts; clean formal history at closeout is
  **3951 attempts / 2812 correct / 2229 unique Q / 1562 touched Nodes**.
- Current formal evidence filtering is applied across adaptive selection, dashboard/navigation,
  field evidence, readiness, pilot diagnostics, subject-detail field views and supporter
  field/weakness views.
- Raw answer-count/time/streak/milestone history remains preserved.
- Phase11 remains **HOLD / Shadow-only**; none of this work promotes it.
- Source-context rewrite CI: **1530 passed / 6 skipped / 1 deselected / 141 subtests passed**.
- Subsequent evidence-consumer PRs also require GREEN CI before merge.
- See `docs/PT_NATURAL_USE_AUDIT_20260922.md` for the audit and clean learner baseline.

## 2026-09-22 PT Question Bank minimum-100 field expansion — CURRENT FORMAL BANK Q2743

- Current formal PT Question Bank on `main`: **Q1-Q2743 / 2743 questions**,
  bank version **`2026-09-b22`**.
- Q2234-Q2743 add **510 LT-original questions** to the 10 fields that were below
  100 questions, so all 18 formal PT fields now have at least 100 questions of
  supply.
- The September 22 expansion is already merged to `main` at
  `253086dbba57d845dc4652a74c1199288d6949c1`; full CI recorded
  **1529 passed / 6 skipped / 141 subtests passed**.
- Render `line-bot-project` auto-deployed that exact commit and the deploy is
  recorded as **live**. No manual deploy is required for this documentation sync.
- The added 510 questions are marked `tag_status=provisional_bulk`. They satisfy
  the formal minimum-supply contract but should not be interpreted as a finished
  editorial-quality claim. Future work may replace or deepen them with independent
  clinical scenarios when learner evidence shows that doing so improves outcomes.
- The prior Q2233 expansion remains a valid historical milestone, but it is no
  longer the current bank boundary. Historical Q2000/Q2233 audit sections below
  must not be read as the current formal range.
- The Notion task "Question Bank分野別供給数の棚卸し・不足分作成" is complete.
  The next default direction is not further uniform volume growth; use real
  learner evidence to prioritize coverage quality, repair/depth supply,
  retention, and exam-readiness work.
- Formal learning-data authority remains:
  `question_attempts -> derived Knowledge Node state -> field/strategy/readiness -> selector/presentation`.
  Phase11 remains HOLD/Shadow-only and must not self-promote.

## 2026-09-20 PT Lifecycle — shadow metadata wiring

- Lifecycle v0.1 remains non-authoritative for question selection. The existing
  Stage E pilot snapshot now derives the pure lifecycle result from the same
  aligned field evidence/targets/formal Node states and observed Critical Safety
  context, then records only diagnostic lifecycle metadata in the existing
  confirmed-answer JSONB payload.
- Added metadata: lifecycle version/phase, initial-coverage checkpoint,
  repair/retention priority flags, reason codes and missing-evidence codes.
  No DB schema/migration is required; no new write path exists.
- Exact-Q selection, Stage E field ranking/reroute, Safety protection, 72-hour
  guard, Recent Cooldown, equivalence, fallback behavior and pilot allowlist are
  unchanged. Phase11 remains HOLD/Shadow-only. No learner-facing UI change.
- Production natural-use inspection found the persisted user_node_state table is
  only a basic cumulative cache and is not the formal lifecycle truth; formal
  lifecycle input remains question_attempts -> derive_all_user_node_states.
  September20 latest wrong answers prove active formal repair demand, so the
  expected current lifecycle phase for the primary learner is depth_repair.
- Acceptance for this wiring requires focused tests/full CI before merge and then
  ordinary pilot natural-use observation; no educational-effect claim is made.


## 2026-09-20 PT Learning Lifecycle — pure model, runtime disconnected

- Baseline main: 289f09edd1392252b60c7b68211431f83396b91a (#393, Q2233).
- Natural-use data observed: Boss supplied anonymous September20 aggregates
  (250 attempts, 156 correct; 76 repair selections; 233 added questions consumed;
  72h same-Q repeats zero). No new Production DB access or acceptance claim.
- Pure lifecycle model code exists in licensetown/pt/learning_lifecycle.py:
  initial per-field coverage checkpoint, current formal repair/Critical Safety
  priority and existing retention signals. No Q-range/accuracy phase gate.
  Missing Safety remains unavailable. Old wrong history does not reopen repair.
- Runtime integration NOT done; production behavior unchanged. No Bank, selector,
  DB/schema, Stage E, Phase11, UI/LINE, environment or Render changes.
  Production acceptance of the model NOT claimed; output remains provisional.
- Focused tests passed: 133 (including 10 lifecycle cases and unchanged field,
  Node, repair/retention, strategy/pilot and Q2233 regressions), Python 3.13.7.
  DATABASE_URL empty and dummy API credentials; no new skips. Q2233 validator:
  all four components 2233 records; missing/duplicates/schema/reference issues 0.
  Local full suite not required for this step; existing PR CI runs it unchanged.
- Contract and Phase 2 boundaries: PT_LEARNING_LIFECYCLE_LEVEL2_V01.md.

## 2026-09-19 PT Question Bank depth expansion Q2233

- Boss explicitly approved expanding the PT formal Question Bank after the primary
  learner effectively completed one full Q2000 pass. The purpose is not uniform
  volume growth; it is reusable Level-2 depth/repair supply for all PT learners.
- Formal PT Question Bank on this branch: **Q1-Q2233 / 2233 questions**,
  bank version **2026-09-b21**.
- Composition: **LT original 1133 / past_exam 1100**. The past-exam inventory and
  repository-frequency Exam Weight remain based on the same 1100 formal past items;
  no missing year provenance is invented.
- Added Q2001-Q2233: **233 LT-original depth questions** attached to 233 audited
  existing derived Knowledge Nodes. Distribution: anatomy4, physiology8,
  medical overview2, internal medicine18, neurology20, pediatrics3,
  basic kinesiology1, movement analysis6, orthopedics3, PT assessment54,
  PT treatment114. Other fields receive no forced equal-fill questions.
- Selection rule for expansion targets: unresolved critical Safety repair supply,
  repeated-past Nodes lacking STRONG alternate evidence, and high-Exam-Weight
  official non-fact singleton Nodes with meaningful depth/Safety demand.
  One-off low-weight fact recall was deliberately not expanded merely for symmetry.
- Every added question has a pre-Q2001 same-derived-Node reference that classifies
  as **DIFFERENT_QUESTION_STRONG** under the existing formal classifier.
  Q2001-Q2233 also have an explicit content-quality FAIL gate and exact-stem
  regression test in `tests/test_q2233_expansion.py`.
- Registry remains 1562 raw Nodes / 1532 canonical represented Nodes.
  Canonical singleton Nodes decrease to 945; multi-question canonical Nodes rise
  to 587. No new Node IDs were fabricated for this expansion.
- Schema/manifest/runtime range and public count handling are updated to Q2233.
  Public source counts are derived from the formal bank instead of hardcoded
  900/1100 figures.
- Historical Q2000 audits/integrators remain valid milestones and are now explicitly
  safe inside a newer formal superset; they must never truncate Q2001+.
- Full Linux/Python 3.13 PR CI after schema/runtime compatibility repair passed.
  A second CI run adds the dedicated Q2233 content/repair tests; exact final run
  and merge/deploy acceptance are recorded in the PR before Production use.
- No Production DB write/migration, Phase11 promotion, Stage E policy change, or
  Render configuration change is part of the expansion. Runtime rollout remains
  normal main merge -> Render auto-deploy -> live verification.

## 2026-09-19 Root compatibility alias cleanup batch 1

- Current baseline: `a275f5bae8716d1719c5c9de4b14940109622525` (merged #388).
  Canonical domains are licensetown/common, licensetown/pt, licensetown/takken.
  The old qualifications package and root data/question_bank are absent;
  older sections below are historical, not the current ownership map.
- Audited all 102 root Python files plus tracked imports, dynamic import/string
  references, test monkeypatches, scripts, docs and startup configuration.
  Complete inventory/retention reasons: ROOT_ALIAS_CLEANUP_BATCH1_20260919.md.
- Removed only adaptive_source_mix.py and readiness_service.py root aliases.
  Their only maintained callers were one test import each; both now use
  licensetown.pt directly. Canonical implementations and assertions unchanged.
  100 root Python files remain: three protected bridges and 97 compatibility
  entries, including the special field_evidence offline file-loader bridge.
- Focused tests: 11 passed. Full baseline and post-change suites each passed:
  1502 passed, 6 skipped, 1 deselected, 141 subtests (16 warnings).
  Bank validator: 2000 questions, zero consistency issues.
  Use Python 3.13, empty DATABASE_URL, dummy credentials,
  fresh pytest temp paths and Git LF archives (core.autocrlf=false per command).
  Host Python 3.14 exposed Flask incompatibility; default temp ACL and CRLF
  checkout caused unrelated baseline failures. No app/test/permission fix or
  new deselection is used to hide these host differences.
- Repository-level regression evidence only; no new live learner acceptance.
  app/database/wsgi, Question Bank/KN contents, selector, Stage E, Phase11,
  Takken, DB/schema and Render configuration are unchanged. No production
  access, migration, worktree cleanup, main merge or additional paid operation.


## 2026-09-19 Qualification separation stage 2: PT active-repair rules

- Baseline main `3e3a31842f3bc5e883f8893e450a9e1d26d19cc3`, merged #369.
  The preceding PR passed full CI; live deployment is reported by Boss and was
  not independently queried here (no Render operations).
- Only `phase11_active_repair_rules.py` is relocated to `qualifications/pt/`.
  It owns PT J2/J3 active weakness candidate thresholds and ordering. It has
  only pure functions and typing imports, no DB/Bank initialization, file paths
  or mutable state. The formal judgment caller and all policies stay unchanged.
- The root path aliases the identical module, retaining public/private globals
  and both import orders. Canonical module/source introspection now points to PT.
  Implementation text/AST is identical; J2/J3 outputs match baseline across
  300 deterministic cases. No production startup or caller import is rewritten.
- Local Python 3.12 focused tests: **124 passed, 16 subtests** (compatibility,
  formal judgment/readiness, provider boundaries, strategy/pilot). Validator:
  **2000 records in every bank component; missing/duplicates/reference/schema
  issues 0; 1562 Nodes**. Full Linux/Python 3.13 CI result is recorded in the PR.
  Local full collection is not repeated after the known Windows lxml execution
  restriction; no policy bypass or new skips are introduced.
- Field evaluation/progress/strategy context remain on the Stage E path. KN
  loaders retain fixed paths; mixed settings/presentation and the non-PT-specific
  ordering helper remain in place. Candidate rationale: qualifications/README.md.
- Code/focused tests verified; no new real-history observation or production
  acceptance claimed. Phase11 remains HOLD/Shadow-only, Stage E pilot unchanged,
  Takken unconfigured. No DB access/migration, Render operation or added charges.


## 2026-09-19 Minimal qualification folder separation

- Baseline main `722afce9ac00e09889822bc09079f2f256b29fad` (#368).
  Existing common/PT/Takken packages and contracts are reused, not recreated.
- PT-only exam weights now live in `qualifications/pt/exam_weight_shadow.py`.
  The legacy root import aliases the same module object. Executable AST and
  all 18 field outputs match baseline; both import orders and patched globals
  are covered. No data, taxonomy, selector or strategy policy was changed.
- `qualifications/README.md` records common contracts, PT ownership, dormant
  Takken and retained runtime composition; Takken README records fail-closed
  provider/store behavior. No fabricated Takken implementation or activation.
- Existing root entry points, data paths, common registries, SQL/session hooks,
  UI and test paths stay in place. Stage E PT pilot and Phase11 HOLD unchanged.
- Local Python 3.12 focused tests: **101 passed, 16 subtests**. Validator:
  **2000 questions/answers/explanations/tags, missing/duplicates/reference
  inconsistencies 0, schema issues 0, 1562 Nodes**.
- Local broad collection is blocked by Windows application-control rejection
  of the existing lxml DLL (42 collection errors), not a test assertion failure.
  Full Linux/Python 3.13 CI evidence is attached to the delivery PR; no execution
  policy changes or test skips were introduced to bypass this host restriction.
- Code/focused tests verified; no new live observation or production acceptance
  is claimed. No production DB access/write, migration, Render operation,
  paid operation, main merge or learning authority promotion.


## 2026-09-15 Stage E pilot mixed-slot supply correction

- Main baseline `70374195f84eee64bd5c6dcd95515b08431a23c0`. SELECT-only
  aggregates confirmed 120 fallback answers from four sessions, with protected
  counts28/28/28/29. The old adapter demanded30 field candidates although only
  2/2/2/1 slots needed filling. Stage E critical Safety scores remained1.
- Adapter now counts only unprotected slots, excludes protected evidence from
  supply/selector candidates, and retains real-shortage/guard fallbacks. A fully
  protected session reports no_unprotected_slots rather than soft_pilot.
- No selector/ranking/Safety/cooldown/bank/app/schema changes; existing pilot
  gates and non-adaptive paths unchanged. No production writes, Render operation,
  migration, main merge or authority promotion.
- Reproduction: four sufficient-supply cases fail with the original function;
  focused regressions **135 passed**. Full local Python3.12 suite **1471 passed,
  6 skipped, 1 deselected, 141 subtests** in52.54s; existing CI external-fixture
  deselection, empty DATABASE_URL and dummy credentials. Validator **2000 records,
  0 issues**, 1562 Nodes.
- Code/tests verified; aggregate production incident observed; exact historical
  start-state replay and corrected live behavior NOT verified. Detailed export
  was blocked by automatic approval review; only aggregate reads proceeded.
  See `PT_STAGE_E_ELIGIBLE_SUPPLY_FIX_20260915.md` for numeric bounds and rollout
  observation requirements. This does not establish learning effectiveness.

## 2026-09-15 Japanese brand-name search reinforcement

- The public `/site` title, application name, Open Graph title and structured
  data now lead with `LicenseTown（ライセンスタウン）` so Google can associate
  the English and katakana brand forms consistently.
- Existing PT exam search intent, canonical URL, description, sitemap, robots,
  visible site UI and runtime behavior remain unchanged.
- This is an indexing signal improvement, not a ranking guarantee. Acceptance
  requires deployment followed by recrawl and a fresh `ライセンスタウン` search.

## 2026-09-15 Qualification three-layer ownership audit

- Baseline main: `30a208a60ca34e23e72e279249713c758e4c0695`.
- `QUALIFICATION_THREE_LAYER_AUDIT_V01.md` maps all 102 root Python modules,
  the complete qualifications package and repository directory families.
- Shared contracts are separated; common registries still import concrete PT
  implementations. This composition exception is documented and retained.
- PT bank provider and Stage E module descriptions now reflect existing pilot
  integration. Five module edits change docstrings only; executable AST is
  identical to baseline. No file moves, import edits or runtime logic changes.
- Takken remains metadata-only and both registries fail closed. A real bank,
  stable IDs, answer/explanation records, reviewed taxonomy/KN/evidence contracts
  are required before extending the dormant qualification.
- No DB/Render/LINE/production operation or Phase11/Stage E promotion. This
  audit does not newly verify live configuration or real learner acceptance.
- Validation: focused qualification/PT/pilot/repeat checks **184 passed**
  (16 subtests); full suite **1460 passed, 6 skipped, 1 deselected**
  (141 subtests), 52.80s on local Python 3.12. DATABASE_URL empty, dummy API
  credentials, PYTHONPATH=. and the same external-fixture deselection as CI.
  CI uses Python 3.13. Bank validator: **2000 records, 0 issues**, 1562 Nodes.
  Existing deprecation warnings remain; no test expectations were rewritten.

## 2026-09-14 Strategy pilot integration preparation — default OFF

- Separate runtime preparation follows accepted Stage F.2 audit #351.
  Existing LINE adaptive30 Node selector gets an optional soft field strategy
  adapter behind ENABLE_LEARNING_STRATEGY_V1 (false) and exact pilot allowlist.
- OFF/non-pilot makes no extra event read or strategy import. Baseline Safety,
  due-retention and #342 exploration choices are retained; remaining choices
  come from the existing selector. Missing context/supply/errors use baseline.
- Existing confirmed-answer JSONB metadata records strategy disposition; no DB
  schema/migration, manual deploy, Render-variable change or Phase11 promotion.
- Code exists and regression tests cover gates/guards/fallback/metadata. CI/live
  delivery evidence is recorded in the PR and final report. Production activation
  is NOT authorized by this preparation and needs a separate explicit decision.
- Contract: `PT_LEARNING_STRATEGY_RUNTIME_PILOT_V1.md`. Web/manual/initial
  assessment remain on current routes. Prospective efficacy remains unproven.

## 2026-09-14 Stage F.2 — PASS WITH CONDITIONS

- Latest main #348/#349 assessed with2655 anonymous PT attempts and14 real plans.
  Raw small-bank states both assessing; Safety contradictions0; eligible30 supply
  14/14 (minimum35); post-#337 repeats0 across645 attempts.
- Physiology plan context0,0,0,1,1; actual penalty0,0,0,1/3,1/3 reduces last two
  scores by0.066667. Safety explains continued recommendation. No observed
  >3-completed-block persistence; such exposure is not empirically proven safe.
- Code/test/real observation: YES. Production activation: NO. This permits only
  separate default-OFF gated pilot preparation; no educational-effect claim.
- Full report: `PT_LEARNING_STRATEGY_STAGE_F2_20260914.md` and companion JSON.
  Prior Stage F HOLD section below is historical and superseded for preparation.

## 2026-09-14 Stage F natural-history audit — HOLD / NOT YET

- Offline replay of 2545 anonymous PT attempts at 85 checkpoints on main #346.
  Top1 agreement 12/83; top3 23/83; eligible30 supply 85/85 (minimum34).
  Critical Safety priority contradictions0; post-#337 observed same/exact repeats0
  across535 attempts. No runtime, selector, DB or authority changes.
- Promotion blockers: maximum26 consecutive recommendation observations;
  additional/consecutive block context unavailable; two small-bank raw weak
  classifications conflict with Stage F's small-supply policy. Audit labels these
  assessing while preserving raw outputs. Current #342 stays accepted and intact.
- Status: code exists YES / audit tests8 PASS / full local suite1433 PASS,
  6 skipped,1 deselected,141 subtests / bank validator2000 records,0 issues /
  real history observed YES / promotion accepted NO.
  Audit/tests/docs delivery is subject to full CI and read-only auto-deploy checks;
  their exact SHA/results are recorded in the delivery PR and completion report.
- Details and all18 field rows: `PT_LEARNING_STRATEGY_STAGE_F_AUDIT_20260914.md`
  and companion JSON. Next work is a separate promotion decision addressing the
  context/policy gaps; do not connect Stage D/E to Production. These are strategy
  promotion blockers, not newly demonstrated PT v1.0 runtime defects.

## 2026-09-14 Learning strategy Stage C/D/E — Shadow only

- Stage C PR #345 merged at `d7d2b6039b4aa45f6f45c6ce1fbbe2fc2af95770`: provisional
  18-field repository-frequency Exam Weight; 900 original / 1100 past_exam;
  year provenance 36, gap 1064. No fabricated historical windows.
- Stage D/E code adds pure field targets and explainable ranked strategy candidates.
  Inputs are existing evidence/progress snapshots plus explicit observed context.
  No Production caller, DB write/schema, selector/session/event-key or UI changes.
- Stage B's 60-answer + canonical-spread gate remains intact. Supply-capped first
  passes, three-block additional ceiling, maintenance and critical Safety are
  separate strategy policies; they cannot authorize Q repeats or bypass #337/#342.
- Status: **code exists: YES / targeted tests: 94 PASS / full local suite: 1425 PASS,
  6 skipped, 1 deselected, 141 subtests / bank validator: 2000 records, 0 issues /
  natural Stage D/E comparison: NOT YET / promotion: NO**. CI and deployment
  acceptance are recorded against the delivery PR/merge SHA; neither promotes authority.
- Phase11 stays HOLD / Shadow only. Missing Safety/timing/concentration context
  and unsupported year windows remain explicit rather than inferred.
- Specification: `docs/PT_LEARNING_STRATEGY_SPEC_V1.md`; roadmap:
  `docs/LEARNING_STRATEGY_ROADMAP_20260913.md`. Next work is natural-history
  comparison and acceptance, not automatic Production promotion.

## 2026-09-10 PR #306 all-path repeat-guard hardening v0.2

- Additional acceptance hardening keeps the formal under-three-day exact-evidence block authoritative across random, category, nekketsu, adaptive daily, and web recommendation starts.
- Category/intent shortages relax progressively to the global non-blocked bank; a missing alternate question skips that Node instead of reopening recent evidence.
- A physically impossible global shortage now fails explicitly with a learner-safe availability response instead of padding with blocked questions or returning an opaque 500/503.
- Selector, Safety priority, repair evidence, retention/state transitions, Phase 11, Question Bank content, and database schema remain unchanged.
- Status: **focused regression: 201 passed, 1 deselected, 125 subtests / Question Bank validator: 2000 records, 0 issues / full LF CI-equivalent pytest: 1283 passed, 6 skipped, 1 deselected, 125 subtests / Production deployed: NO / real learner acceptance: PENDING**.

## 2026-09-10 Production blocker: global short-term same-Q repeats

- Production attempts showed the same evidence question recurring within minutes through non-adaptive learner paths, despite the adaptive Recent Cooldown repair.
- Root cause: the PR #296 protection lived inside the adaptive/daily selectors; ordinary random/category session creation and prerequisite backtrack did not consistently apply the authoritative `question_attempts` history.
- Fix branch: `fix/global-short-term-repeat-guard-v01`. All ordinary learner session paths now derive one shared blocked exact-evidence set from formal Node-state replay. Previously attempted evidence stays blocked until the formal state is `recheck_due`; same-Node different-Q repair remains eligible.
- Random/category selection accepts that blocked set, category shortage fills from other non-recent evidence instead of immediately repeating a Q, and prerequisite backtrack cannot reinsert blocked evidence. Initial assessment remains unchanged.
- Status: **real Production defect observed: YES / cause identified: YES / focused regression: 173 passed plus 125 subtests / LF CI-equivalent full pytest: 1268 passed, 6 skipped, 1 deselected, 125 subtests passed / Production deployed: NO / real learner acceptance: PENDING**.

Last updated: 2026-09-10
Safe integration base: `work/pt-finalization-post-q2000`

## How to resume
1. Read `AGENTS.md`.
2. Read this file.
3. Read `docs/PT_V1_PRODUCT_GOAL.md`.
4. Verify only facts affected by newer commits/data.
5. Continue from the open work instead of rediscovering the repository.

Always distinguish: **code exists / tests pass / real data observed / product accepted**.
Do not casually change `main`, Production Neon, Render or LINE behavior.
Practical learner effect and national-exam success outrank architectural elegance.

## 2026-09-10 Production blocker: global short-term same-Q repeats

- Production evidence showed same raw questions recurring within minutes across ordinary learning sessions, including Q1702 at 17:34 / 17:39 / 17:45 and Q1595 at 19:16 / 19:24.
- PR #296 protected the Node-adaptive and legacy daily builders, but ordinary random/category starts and prerequisite backtrack still had paths that did not apply the formal attempt-based guard.
- Fix branch: `fix/global-short-term-repeat-guard-v01`. Every non-initial-assessment start reads `question_attempts` as formal truth, canonicalizes exact-repeat evidence identity, and blocks previously attempted evidence until the formal Node replay reaches `recheck_due`; same-Node different-Q repair remains eligible.
- Random/category selection accepts the same evidence exclusions, and prerequisite backtrack cannot inject a blocked recent evidence question. Initial assessment remains on its fixed contract.
- Status: **real Production defect observed: YES / code fix exists: YES / focused regression green / full CI pending / Production deployed: NO / real-device acceptance: PENDING**.

## Fixed PT v1.0 product finish line

Boss and Aoi fixed the shared definition of **「修正は今後もあるが、一旦完成として商品として出せる物」** on 2026-09-09.

The authoritative detailed contract is `docs/PT_V1_PRODUCT_GOAL.md`.

Do not broaden the finish line in later chats merely because another improvement is possible. New findings must be classified as either:
- **v1.0 product blocker**, or
- **v1.1+/backlog**.

PT v1.0 is considered product-ready when a new learner can register, study, have attempts saved, receive weakness-aware next study, pause/resume safely, understand what to do today, and complete ordinary learning without serious data-loss/study-blocking defects; required automated checks are green; production-equivalent flow works; and several days of real use show no major blocker.

The completion target is not perfection, complete long-term proof, or implementation of every future feature.

## Public Question Bank display

- Public marketing stats must show the closed Q2000 composition as **新規問題 900問 / 過去問 1100問 / 合計 2000問収録**.
- Do not expose stale preview-source counts such as 643 / 1094.

## 2026-09-09 Production blocker: 合格への道 500

- Real learner reported HTTP 500 on `/goukaku-no-michi`. Render traceback confirmed `ValueError: attempts must belong to one user and one canonical Node`.
- Root cause: `phase11_active_weakness.build_active_repair_weakness()` grouped histories by raw/canonical Knowledge Node only, while exact-repeat evidence can deliberately remap a question to a different derived evidence Node (`Q1585`: raw `KN0659` -> evidence `KN1387`). This mixed two evidence Nodes in one history and violated the formal state-transition invariant.
- Fix branch: `fix/goukaku-500-evidence-node-grouping-v01`. Group active-weakness histories by `canonicalize_question_evidence_node(question_id, raw_node_id)` so grouping matches the same derived evidence authority used by `knowledge_node_state_transition.py`.
- Regression coverage explicitly includes the cross-node exact-repeat case.
- Resolution status: **real Production failure observed: YES / root cause identified: YES / targeted regression: 21 passed / full CI run #632: 1233 passed, 6 skipped, 1 deselected, 125 subtests passed / PR #288 merged to main at `c1209ebb2c7a38df95e532831e5a31e49cff400d` / Render deploy `dep-dagjv59srm7s73fh96ug`: live / real post-fix learner-device acceptance: PENDING**.

## 2026-09-09 Dashboard whitespace defect

- Real learner screenshot after the `/goukaku-no-michi` 500 repair showed a large unnecessary blank region in the right story column beside `学習の現在地`.
- Cause: `dashboard-layout-v05.js` kept `学習の現在地` in the taller left column but forcibly moved the 7-day learning card to a new full-width row below the two-column story. CSS Grid therefore had to preserve the left-column height and left a large empty right area.
- Fix branch: `fix/dashboard-blank-space-v01`. Keep `学習の現在地` on the left and place the 7-day learning record into the right story stack so the existing space is used naturally; mobile remains one-column through the existing breakpoint.
- Status: **real Production screenshot observed: YES / root cause identified: YES / code fix under validation / Production accepted: NO**.

## 2026-09-09 Dashboard approved production layout

- Boss approved the final desktop composition for `/goukaku-no-michi`: the large `合格までの推奨ルート` is placed immediately below the top date/exam/progress summary and before the daily-action/navigation area.
- No learner-facing information card may be deleted to make the route larger. The preserved content set includes `今日やること`, `分野別到達度`, `源さんの一言`, `知識の確認状況`, `今の学習カルテ`, `定着までの進み方`, `直近7日間の学習記録`, `LTの作戦メモ`, `学習の現在地`, `あなたの足跡を見る`, and `次のチェックポイント`.
- Desktop story rails are intentionally balanced: left = field progress -> LT strategy memo -> learning position -> footprints; right = Gen-san -> knowledge status -> learning chart/profile -> retention flow -> weekly record -> next checkpoint. Mobile remains a single-column flow.
- The formal Gen-san production asset remains `static/images/characters/gensan_main.png`; generated mockup faces are never production assets.
- Implementation branch: `fix/dashboard-approved-layout-v01`, using `dashboard-approved-layout-v01.js/css` loaded last so the approved hierarchy wins over older layout scripts without deleting their content-generation logic.
- Status: **Boss layout approval: YES / code exists: YES / automated validation pending / Production deployed: NO / real-device acceptance: PENDING**.

## 2026-09-09 Dashboard reference-halves correction

- The previous PR #291 production layout did not reproduce Boss's two attached reference screenshots faithfully and produced a broken/chaotic visual composition in real use. That production acceptance is revoked.
- Boss supplied two screenshots that together define the desktop layout: top half = date/priority on the left with overall progress on the right, then summary, learner decision/navigation, and the large `合格までの推奨ルート`; lower half = `分野別到達度` opposite `源さんの一言` -> `知識の確認状況` -> `今の学習カルテ` -> `定着までの進み方`, then `LTの作戦メモ` + `学習の現在地` opposite `直近7日間の学習記録`, finishing with `あなたの足跡を見る` and `次のチェックポイント`.
- No learner-facing card is deleted. The formal Gen-san asset remains `static/images/characters/gensan_main.png`.
- Corrective branch: `fix/dashboard-match-reference-halves-v01`. `dashboard-approved-layout-v01.js/css` is now a final deterministic override loaded last; desktop uses explicit top and lower grids, mobile remains one column.
- Status: **real Production defect observed: YES / Boss reference supplied: YES / corrective code exists: YES / automated validation pending / Production deployed: NO / real-device acceptance: PENDING**.

## 2026-09-09 Dashboard upper-reference lock

- Boss supplied a new authoritative screenshot for the **upper half only** and explicitly froze the previously approved lower half. No independent layout judgement is allowed.
- Upper desktop order is fixed to: left column `date-card -> 今日やること`, right column `合格への到達度`; then full-width `summary-grid`; then full-width `合格までの推奨ルート`; then full-width current/priority overview (`learner-current-card`).
- The redundant source-only learner navigation remains in DOM for data/behavior but is not a visual layout authority; its visible `today` and `current` cards are moved into the approved positions.
- Lower desktop composition is unchanged from the preceding Boss-approved screenshot and is treated as frozen: subjects / Gen-san / knowledge state / study profile / retention / LT strategy / weekly record / learning position / footprints / checkpoint.
- Formal Gen-san production asset remains `static/images/characters/gensan_main.png`. Mobile remains one column.
- Corrective branch: `fix/dashboard-upper-reference-only-v01`; asset cache version bumped to `20260909-v03`.
- Status: **Boss upper reference supplied: YES / lower half frozen: YES / code exists: YES / automated validation pending / Production deployed: NO / real-device acceptance: PENDING**.

## 2026-09-09 Dashboard summary-row production correction

- Real Production screenshot showed PR #294 did not visually satisfy Boss's instruction: the five summary cards still wrapped 3+2 on wide desktop and the new route-card guidance could be hidden by stale asset cache.
- Root cause: the five-column override was scoped only to 701-1000px, so widths above 1000px fell back to the legacy three-column rule; `dashboard-product-copy-v01.js` and the approved-layout CSS cache keys were also not bumped.
- Corrective branch: `fix/dashboard-summary-row-cache-v01`. For every viewport >=701px the summary grid is forced to five columns in the fixed order already present in the DOM: total answers / cumulative study time / 7-day accuracy / average accuracy / consecutive learning days. Mobile <=700px is unchanged.
- Route top-card guidance remains the PR #294 copy and is now forced fresh by cache-key updates. No lower-half layout or other dashboard composition is changed.
- Status: **real Production mismatch observed: YES / root cause identified: YES / code fix exists: YES / automated validation performed in branch workflow / Production deployed: NO / real-device acceptance: PENDING**.

## Current completion contract — MAIN LINE ONLY

Until PT v1.0 is accepted, do not drift into speculative polish or branch/leaf work.

Car model:
- **走る**: quiz -> answer -> save -> score -> explanation -> continue.
- **曲がる**: next questions change according to real weakness/repair/retention state.
- **止まる**: pause/resume/end/reset safely.
- **壊れない**: formal question/history/Node/session invariants stay coherent.
- **壊れた所を特定できる**: evidence shows which Q/Node/state/selection caused the issue.
- **特定したら修復できる**: learner weakness returns through repair and spaced retention; system defects are reproducible and safely fixable.

Core learner loop:

`wrong -> observable wrong-pattern analysis -> same-Node/different-Q repair -> repair confirmation -> day3 -> day7 -> one-month -> durable OR back to repairing`

A candidate change is in scope now only when it fixes a real current defect, is necessary for this main line, or directly changes learner outcome. Otherwise backlog it.

---

# 1. Question Bank / Q2000 — CLOSED

- Formal PT Question Bank: **Q1-Q2000 / 2000 questions**.
- Bank version: **`2026-09-b20`**.
- Final cross-sectional medical/editorial quality audit is closed on the safe post-Q2000 branch.
- 33 same-stem groups resolved to 29 legitimate same-stem/different-choice official items plus 4 exact official provenance repeats.
- Exact-repeat groups: Q972/Q1354, Q1067/Q1391, Q1230/Q1526, Q1411/Q1585.
- Raw official Q IDs/provenance remain immutable, but exact repeats are one derived learning-evidence identity through `question_equivalence_groups.json`.
- Equivalent official repeats cannot inflate cross-question weakness, STRONG repair confirmation, or Recent Cooldown behavior.
- Q1411/Q1585 cross-Node identity is reconciled only in derived evidence under KN1387; raw Production rows are unchanged.
- KN0597/KN0807 duplicate raw label is already resolved by reviewed canonical alias KNC0001.
- KN1142/KN1252 share a generic label but are medically different concepts; do not merge.
- Q2000 final-quality PR #277 was merged only to this safe branch. No `main`/Production promotion occurred.

Detailed record: `reports/q2000_final_quality_review_20260909.md`.

---

# 2. Formal learning-data authority

Formal truth path:

`question_attempts -> derived Knowledge Node state -> field/strategy/readiness -> selector/presentation`

- `question_attempts` is the authoritative durable attempt history.
- `user_node_state` is not formal truth.
- Formal Node state is pure-derived by `knowledge_node_state_transition.py`.
- Question equivalence is applied only to derived evidence; raw history is preserved.

Primary learner Production snapshot measured 2026-09-09:
- **1525 attempts**
- **1103 correct / 72.3%**
- **740 unique questions**
- **572 unique raw Knowledge Nodes**
- observation window: 2026-08-17 through 2026-09-09 JST

Detailed real-history analysis: `reports/primary_learner_history_analysis_20260909.md`.

Important learner-history findings:
- confidence 1: 850 attempts / 88.5% accuracy;
- confidence 2: 623 / 54.3%;
- confidence 3: 42 / 31.0%;
- confidence-1 wrong: 98 high-value misconception/repair candidates;
- confidence-2/3 correct: 351 uncertain-correct/checking candidates;
- 344 questions were attempted at least twice;
- first wrong -> latest correct: 76;
- first correct -> latest wrong: 52;
- first wrong -> latest wrong: 37;
- first correct -> latest correct: 179.

Conclusion: confidence and longitudinal transitions are materially informative. Do not reduce learner state to raw accuracy alone. Do not expand above Q2000 merely to add volume.

---

# 3. Core repair / retention loop — CODE + TESTS COMPLETE

Formal repair semantics:
- any evaluable wrong or `unknown` starts/returns the Node to `repairing`;
- same-Q correct does **not** confirm repair;
- weak different-Q correct does **not** confirm repair;
- repair confirmation requires **STRONG different-Q + confidence=1**;
- exact official equivalent repeats are one evidence identity and cannot fake different-Q confirmation.

Spaced retention contract implemented in `knowledge_node_state_transition.py`:
1. STRONG different-Q confidence=1 after wrong -> `repaired`, next check at **3 days**.
2. Valid day3 check before day7 horizon -> `day3_passed`, next check at **7 days** from repair confirmation.
3. Valid check on/after day7 horizon -> `stable`, `day7_passed`, one-month check scheduled.
4. Valid one-month check -> remains `stable`, `durable`, no further required checkpoint in v0.1.
5. Wrong/unknown at any retention checkpoint -> fresh `repairing` cycle and old retention schedule is cleared.
6. If the learner misses day3 and first valid spaced check happens on/after day7, it counts as the day7 horizon instead of manufacturing an overdue backlog.

Selector integration:
- `recheck_due` is an explicit checking priority;
- an actually due time-based retention check may deliberately bypass last-30-attempt Recent Cooldown;
- this bypass is saved as `recent_cooldown_bypassed=True` for auditability;
- ordinary recent-repeat avoidance and Safety behavior remain intact.

Wrong-pattern analysis is evidence-based, not a hidden psychological diagnosis. `companion_record.py` can classify:
- retention regression;
- confidence-1 wrong;
- repeated cross-question wrong;
- repeated same-question wrong;
- unknown answer;
- uncertain wrong;
- single wrong.

It explicitly declares `wrong_pattern_semantics = observable_evidence_not_psychological_diagnosis`.

PR #285 was merged into `work/pt-finalization-post-q2000` at merge commit `314813170a4b25897136e9d67f24428931f24bfa` after GREEN CI.

Full validation on the core implementation:
- **1232 passed**
- **6 skipped**
- **1 deselected**
- **125 subtests passed**
- run #626: GREEN
- run #627 after the state-document update: GREEN

Evidence boundary:
- **code exists: YES**
- **full tests pass: YES**
- **natural learner day3/day7/one-month sequence observed end-to-end: NOT YET**
- **Production behavior deployed/accepted: NO**

The missing natural 3d/7d/one-month evidence is time-dependent evidence, not a reason to keep adding speculative code before v1.0 acceptance.

---

# 4. Phase11 strategy engine — HOLD / Shadow-only

Implemented strategy intents include Safety repair, confident/repeated wrong repair, ongoing repairing, retention recheck, uncertain checking, coverage expansion and maintenance.

Boundary:
- Phase11 decides **what / why / how many / intent**.
- Phase10/selector owns **which exact Q**.

PR #284 closed an actual main-line gap: learner navigation `learning_intent` now reaches web recommendation session and exact-Q adaptive selection. Explicit `repair`, `recheck`, and `exploration` intents fill the matching selector group first; normal callers without explicit intent retain mixed composition.

Automatic evidence before this core-loop update:
- repeat audit: PASS;
- Critical Safety retrospective: PASS-to-date;
- J2/J3 trigger consistency: PASS;
- current profile consistency: PASS;
- retrospective replay coverage for current recommendation anchors: PASS;
- current automatic FAIL/BLOCKED gates: none.

Still OPEN where real natural/prospective evidence is required:
- natural spaced retention outcome under the new day3/day7/one-month contract;
- natural `recheck_due` intent -> exact-Q alignment;
- retrospective comparison diversity;
- prospective learner relevance vs baseline;
- final human promotion review.

Do not self-promote Phase11. Do not keep coding just to force these time-dependent gates closed.

Detailed record: `reports/phase11_promotion_review_20260909.md`.

---

# 5. Adaptive selector / Recent Cooldown

- Node-level adaptive selection works.
- STRONG different-question repair can be preferred.
- Formal learner `repair/recheck/exploration` intent reaches exact-Q selection.
- Recent Question Cooldown avoids gratuitous recent repeats.
- Time-based `recheck_due` can bypass cooldown intentionally so a scheduled retention check is not starved by the large bank.
- Adaptive audit metadata persists selection reason/group/score, repair evidence quality, recent repeat and cooldown bypass.
- Current learner history shows no unexplained or internally inconsistent adaptive-repeat defect.
- Exact official repeats share one evidence identity for selection/cooldown interpretation.

No further selector polish is in scope unless real use exposes a main-line defect.

---

# 6. Dashboard / learner navigation — v0.1 CONSOLIDATED

Learner route `/goukaku-no-michi` builds formal learner navigation from authoritative attempts/readiness/shadow evidence.

Completed consolidation v0.1:
- top `現在地`, `今日やること`, formal priority TOP3, repair/coverage/retention guidance are the learner-facing decision authority;
- duplicate lower legacy TOP3/recommendation are hidden when formal learner navigation exists;
- legacy field percentages, when shown, are labeled **`分野別 正答率（参考）`**, not formal `到達度`;
- factual counters remain factual counters.

Source map: `reports/dashboard_source_map_20260909.md`.

Dashboard polish is **not current main-line work**. Only learner-facing contradictions or missing v1.0-required guidance can block productization.

---

# 7. Longitudinal companion record — CORE EVIDENCE LAYER IMPLEMENTED

`companion_record.py` derives compact longitudinal episodes from `question_attempts`; it does not create a second persisted truth.

Current core-useful fields/events include:
- weakness detection;
- observable wrong pattern;
- repair confirmation;
- retention stage/checkpoint/next review;
- day3/day7 checkpoint pass;
- retention due;
- durable retention confirmation;
- regression back to repairing.

Do not build a large journal UI for v1.0. Only expose the minimum learner-facing summary needed to answer: where weak / how wrong / repaired or not / next review / regressed or not.

---

# 8. Learning-time/session linkage — DEFERRED

- Learning time persists separately.
- Current `attempt_position` resets inside 5-question batches, so `question_attempts` alone cannot validly measure position 1-30 fatigue in a 30-question session.
- `:time`-style event keys may intentionally differ for idempotency; do not treat event-key equality as a relational join.
- Add explicit durable session linkage only if real use shows it changes learner outcome.
- This is not a v1.0 product blocker by itself.

---

# 9. PT v1.0 remaining path

The coding task for the repair/retention core is CLOSED. Do not invent another engineering subproject just because the core can be polished further.

The next work must be judged only against `docs/PT_V1_PRODUCT_GOAL.md`.

Remaining productization path:
1. verify the complete learner-facing path on the safe branch against the v1.0 checklist: registration -> study -> answer/save -> score/explanation -> pause/resume -> next-study guidance;
2. expose only the minimum weakness/repair/next-review information needed for a learner to know what to do, if current UI does not already make it clear;
3. prepare/promote the already-tested main-line changes to a production-equivalent environment using normal safety rules;
4. run real-device acceptance with the primary learner for several days;
5. fix only observed **v1.0 blockers**;
6. once no serious study-blocking defect remains, declare **LicenseTown PT版 v1.0 商品化完了** even if v1.1 improvements remain.

Not v1.0 blockers by default:
- full long-term Phase11 proof;
- completion of every day3/day7/month natural evidence pattern;
- large companion/journal UI;
- dashboard polish beyond contradiction-free guidance;
- session/fatigue analytics;
- future HP/Town/avatar/social features;
- speculative safety work for unobserved edge cases.

Do not restart Q2000 audit, question-count expansion, speculative branch work, or unrelated product expansion unless Boss explicitly reprioritizes them or real main-line evidence exposes a genuine v1.0 defect.
