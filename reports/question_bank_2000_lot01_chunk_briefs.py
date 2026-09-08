"""Generate compact Codex-ready authoring briefs for the six Lot01 chunks."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "staging" / "question_bank_2000_lot01_chunks_v01"
OUT_DIR = ROOT / "docs" / "question_bank_2000_lot01_chunk_briefs_v01"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_brief(index: int) -> str:
    payload = read(CHUNK_DIR / f"chunk_{index:02d}.json")
    rows = []
    for d in payload["drafts"]:
        rows.append(
            f"- `{d['draft_id']}` | cat {d['proposed_category_small']} | {d['slot_type']} | "
            f"Node `{d.get('target_node_id')}` | refs {', '.join(d.get('reference_question_ids', [])) or '-'} | "
            f"suggested `{d.get('proposed_task')}/{d.get('primary_ability')}` | level {d.get('level')} | safety {d.get('safety')}\n"
            f"  - target: {d.get('target_node_label', '')}"
        )
    roster = "\n".join(rows)
    return f"""# Codex brief — Question Bank 2000 Lot01 / Chunk {index:02d}

This is **authoring chunk {index}/6 only**. It is not an independently integrable batch. Formal baseline is Q1-Q1761.

## Edit exactly

`staging/question_bank_2000_lot01_chunks_v01/chunk_{index:02d}.json`

Change top-level `status` to `completed_chunk` only when all eight drafts are genuinely complete.

## Mandatory repository context

Before authoring, read:

1. `docs/question-bank-2000-lot01-authoring-contract-v01.md`
2. `reports/question_bank_2000_lot01_validate.py`
3. each listed formal reference question, answer, explanation and tag
4. relevant formal-bank questions/Node labels found during semantic duplicate search

## Eight drafts

{roster}

## Required for every draft

- medically sound PT national-exam-level stem and exactly five choices;
- single-best answer unless an explicit, validator-compatible exception is justified;
- concise correct-answer explanation and explanation for all five choices;
- clinical intent;
- trustworthy HTTPS medical evidence with support notes;
- semantic duplicate search against Q1-Q1761 and the other seven drafts;
- `semantic_review.why_not_same_demand`, related formal Q IDs, decision, reviewer/date and expert_signoff completed honestly;
- for existing Nodes, the actual semantic demand must differ from all listed existing `(task, primary_ability)` demands, not merely the metadata label.

Suggested task/level/Safety fields are starting points, not permission to force an implausible question. If one must change for medical quality, record the reason in the draft and leave final 48-question quota reconciliation for the full Lot01 merge stage.

## Hard prohibitions

- no formal Q IDs;
- no formal Question Bank edits;
- no Knowledge Node registry edits or new KN IDs;
- no DB/Render/LINE/selector/Phase11 writes;
- no validator/test weakening;
- no fabricated citations, duplicate checks or signoff;
- no merge to main.

## Before commit

Run a JSON parse check and inspect all eight drafts for blanks. Do **not** run the 48-question seal yet. Commit/push only this completed chunk plus any strictly necessary authoring notes. Keep PR #268 Draft.
"""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for index in range(1, 7):
        (OUT_DIR / f"chunk_{index:02d}.md").write_text(build_brief(index), encoding="utf-8")
    print(json.dumps({"briefs": 6, "out": str(OUT_DIR.relative_to(ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
