"""Set required prerequisite statements for Lot03's five new Knowledge Nodes.

The Lot03 integrator allocates the formal Q/KN identifiers first. This idempotent
post-integration step supplies the non-empty prerequisite_nodes required by the
formal question-tag schema before bank-wide validation.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
TAGS = BANK / "question_tags.json"
MANIFEST = BANK / "bank_manifest.json"

PREREQUISITES = {
    "Q1901": (
        "KN1547",
        "肺葉は葉気管支により換気され、葉気管支はさらに区域気管支へ分岐する。",
    ),
    "Q1902": (
        "KN1548",
        "心拍出量は全身へ送り出される血流量を表し、循環機能を評価する基本指標である。",
    ),
    "Q1903": (
        "KN1549",
        "炎症では急性期反応物が変化し、血液検査を用いて炎症活動性の推移を評価できる。",
    ),
    "Q1904": (
        "KN1550",
        "体位変換に伴う血圧低下は、めまい・失神・転倒などの症状や安全性に関係し得る。",
    ),
    "Q1905": (
        "KN1551",
        "歩行開始では静止立位から第一歩へ移るために、重心と足圧中心を調整する姿勢制御が必要である。",
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
    if (manifest.get("question_count"), manifest.get("last_question_number")) != (1905, 1905):
        raise ValueError(f"Lot03 formal integration is not complete: {manifest}")

    tags = _read(TAGS)
    by_id = {row["id"]: row for row in tags}
    changed = 0
    for qid, (node_id, statement) in PREREQUISITES.items():
        row = by_id.get(qid)
        if row is None:
            raise ValueError(f"missing formal tag: {qid}")
        if row.get("knowledge_node_id") != node_id:
            raise ValueError(f"{qid}: expected {node_id}, got {row.get('knowledge_node_id')}")
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
