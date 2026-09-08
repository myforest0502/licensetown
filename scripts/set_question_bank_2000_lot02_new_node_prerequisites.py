"""Set the required prerequisite statements for Lot02's four new Knowledge Nodes.

The Lot02 integrator deliberately allocates the new Q/KN identifiers first. This
small idempotent post-integration step supplies the non-empty prerequisite_nodes
required by the formal question-tag schema before the bank-wide validator runs.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
TAGS = BANK / "question_tags.json"
MANIFEST = BANK / "bank_manifest.json"

PREREQUISITES = {
    "Q1854": (
        "KN1543",
        "高カリウム血症は心筋の興奮性に影響し、心電図変化や致死的不整脈を生じ得る。",
    ),
    "Q1855": (
        "KN1544",
        "発達評価では、既に獲得した技能が維持されているか失われているかという経過情報が重要である。",
    ),
    "Q1856": (
        "KN1545",
        "うつ病では活動回避が機能低下を維持し得るため、活動と気分の関係を評価する。",
    ),
    "Q1857": (
        "KN1546",
        "立ち上がりには、離殿前に身体重心を足部の支持基底面へ移すための前方重心移動が必要である。",
    ),
}


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_preserving_bom(path: Path, payload) -> None:
    raw = path.read_bytes()
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.write_bytes((b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"") + encoded)


def apply() -> int:
    manifest = _read(MANIFEST)
    if (manifest.get("question_count"), manifest.get("last_question_number")) != (1857, 1857):
        raise ValueError(f"Lot02 formal integration is not complete: {manifest}")

    tags = _read(TAGS)
    by_id = {row["id"]: row for row in tags}
    changed = 0
    for qid, (node_id, statement) in PREREQUISITES.items():
        row = by_id.get(qid)
        if row is None:
            raise ValueError(f"missing formal tag: {qid}")
        if row.get("knowledge_node_id") != node_id:
            raise ValueError(
                f"{qid}: expected {node_id}, got {row.get('knowledge_node_id')}"
            )
        expected = [statement]
        current = row.get("prerequisite_nodes")
        if current == expected:
            continue
        if current not in (None, []):
            raise ValueError(f"{qid}: refusing to overwrite existing prerequisites: {current}")
        row["prerequisite_nodes"] = expected
        changed += 1

    if changed:
        _write_preserving_bom(TAGS, tags)
    print(json.dumps({"updated": changed, "questions": sorted(PREREQUISITES)}, ensure_ascii=False))
    return changed


if __name__ == "__main__":
    apply()
