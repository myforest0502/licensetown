# Question Bank 2000 — finish runbook v0.1

## Objective
Reach a **formally validated Q1-Q2000 bank** without trading away medical quality, duplicate safety, Knowledge Node integrity, schema/manifest integrity, or CI. Only after formal Q1-Q2000 is green may the public HP be changed to say `合計2000問`.

## Non-negotiable gates

- No public `2000問` claim before formal Question Bank count is exactly 2000 and validators/CI are green.
- No fabricated medical evidence or human-expert signoff.
- Do not weaken duplicate/semantic validators.
- Do not allocate formal Q IDs during authoring chunks.
- Formal integration must update the four formal stores, Knowledge Nodes where required, manifest/schema/range contracts atomically.
- Recalculate remaining allocation after each formal lot; do not assume planned counts survived content review unchanged.
- Keep normal learner runtime, DB, Phase10/11 and Render behavior unchanged during staging authoring.

## Current baseline

- formal: Q1-Q1761 / 1761
- remaining: 239 = original 233 + past_exam 6
- Lot01 planned: 48 original
- Lot01 authoring: Chunk01 + Chunk02 complete (16/48); Chunk03 is next
- Lot01 chunks: 6 x 8 questions

## Efficient Codex operating rule

Use **one 8-question authoring chunk per Codex run**. Each run reads only:

1. the current chunk file;
2. its exact formal references and related Node data;
3. the chunk validator and similarity-audit contract;
4. concise authoring contract.

Do not load the entire repository into the prompt. Let repository files carry the specification.

## Phase A — finish Lot01 staging

Run Codex separately for Chunk03, Chunk04, Chunk05, Chunk06 using `docs/question-bank-2000-lot01-codex-brief-v01.md`.

After all 6 chunks are complete:

- merge chunks to 48-question staging;
- seal;
- final Lot01 validator;
- formal-bank duplicate/semantic audit;
- relevant tests + full CI equivalent;
- keep PR Draft until staging is fully green.

## Phase B — Lot01 formal integration

Create a separate formal-integration branch/PR from latest main. Integrate the validated 48 questions as the next contiguous Q IDs. Allocate new Knowledge Node IDs only for validated new-Node drafts. Prove existing-node different-demand strong pairs with the runtime classifier where applicable. Update formal stores/Node registry/manifest/schema together. Run full CI. Merge only green.

Immediately after merge, re-run the deterministic remaining-allocation audit against the actual formal bank.

## Phase C — remaining original lots

Planned lot sizes from the pre-Lot01 allocation are 48 / 48 / 48 / 41 after Lot01, but each lot must be regenerated from the actual post-merge formal state.

For each lot:

1. generate deterministic targets and exact quota assignment from the current formal bank;
2. split into 8-question chunks (final chunk may be smaller for the 41-question lot);
3. author one chunk per Codex run;
4. run chunk validator + similarity audit;
5. merge/seal/final-validator whole lot;
6. formal integrate on a separate branch/PR;
7. full CI + merge;
8. recalculate remaining allocation before the next lot.

Prefer existing singleton-second and weak/multi reinforcement where the audit demands it; new Nodes only where the current gap audit reserves them and semantic collision review passes.

## Phase D — past_exam +6

Treat the remaining six past-exam questions as a separate evidence/import track. Use official/public authoritative exam material where legally and technically available. Preserve official answer provenance. Do not invent missing official data. Run the existing past-exam import and Question Bank consistency gates. Formal count must end exactly at 2000.

## Phase E — final 2000 seal

Require all of the following before public claim:

- formal count exactly 2000;
- contiguous Q1-Q2000 across question/answer/explanation/tag stores;
- missing 0 / duplicate ID 0 / cross-store mismatch 0;
- Knowledge Node reference errors 0;
- schema/manifest/range exact at 2000;
- duplicate/semantic audits acceptable;
- full CI green;
- production deploy on the exact merged main commit confirmed.

## Phase F — HP update

Only after Phase E is green, change the HP wording to `合計2000問` (or the approved final copy) on a separate small PR. Do not bundle marketing copy with the bank integration. Verify PC/mobile/724px presentation and production deploy.
