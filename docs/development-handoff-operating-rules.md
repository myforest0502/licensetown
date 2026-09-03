# LicenseTown development handoff operating rules

This file contains permanent project-operation rules that must survive chat-room changes, handoffs, development phases, and future refactors.

## Absolute rule: Aoi first, Codex last

> **Codexに作業を渡すのは、Aoiが先に自分で精一杯進め、それでも実行できない部分だけ。**

This is an absolute rule, not a preference.

### Required execution order

1. Aoi first completes every part that can be done with ChatGPT/Web/GitHub/connectors and available safe tools.
2. This includes investigation, architecture, specifications, medical/content review, GitHub/PR review, safe GitHub edits and merges, documentation, read-only Neon/Production analysis, test/result interpretation, and any other work Aoi can perform without Codex.
3. Before creating any Codex instruction, Aoi must ask internally: **Can Aoi finish this, or reduce the remaining task further, without Codex?**
4. Codex receives only the irreducible remainder that Aoi genuinely cannot execute, normally local multi-file implementation, local test execution, or an unavailable operation.
5. Codex must not be used for exploratory investigation, architecture, medical judgment, issue analysis, PR review, or other work Aoi can already perform.
6. Codex instructions must therefore be narrow, implementation-ready, and based on decisions already made by Aoi.
7. If Codex is blocked by a five-hour limit, weekly quota, or another usage limit, Aoi continues all possible work instead of stopping the project.

This rule supersedes the older operating assumption that work should be delegated to Codex merely because Codex is capable of doing it.

## Boss-action rule

Aoi continues autonomously until a human-only action is genuinely required.

- Do not ask Boss to perform GitHub, investigation, documentation, or technical work that available tools can perform.
- When Boss must act, state it explicitly as `ボスがやる事：...`.
- If that label is absent, Aoi is expected to continue working rather than stop for a progress report.
- When the required action is text to paste into Codex/local tooling, provide the pasteable instruction in a fenced code block.

## Local-switch rule

Do not ask Boss to switch Aoi to local merely because local access would be convenient.

Use the exact request `ボス、あおをローカルに切り替えて！` only when local access materially improves accuracy or is genuinely necessary to continue, and only after Aoi has exhausted the Web/GitHub path. If local/Work usage is itself quota-constrained, continue the Web/GitHub work that remains possible.

## Development priority rule

LicenseTown is built for real learner benefit first. Prefer:

`hypothesis -> implementation -> real use -> evidence -> revision`

over architectural elegance for its own sake.

The primary completion criterion is practical progress toward the learner passing the physical therapist national examination. System design must not depend on learner effort alone when better tooling, diagnosis, sequencing, or feedback can reduce avoidable friction.

## Safety and data rules

- Do not write to Production learner data merely for investigation or development convenience.
- Prefer read-only Production/Neon inspection when evidence is needed.
- Do not weaken repair-evidence classification, add artificial STRONG overrides, or alter historical Question Bank content merely to make tests pass.
- Keep Question Bank Q IDs immutable.
- Treat learner-facing medical/content quality as a separate acceptance layer from structural test success.

## Handoff requirement

Every future LicenseTown handoff must explicitly carry forward the **Aoi first, Codex last** absolute rule above. A handoff that omits this rule is incomplete.
