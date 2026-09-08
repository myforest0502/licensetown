"""Set prerequisite statements for Lot04's four new Knowledge Nodes after formal integration."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "data" / "question_bank"
TAGS = BANK / "question_tags.json"
MANIFEST = BANK / "bank_manifest.json"

PREREQUISITES = {
    "Q1950": (
        "KN1552",
        "腕神経叢は主にC5〜T1神経根から形成され、末梢神経を介して上肢・肩甲帯の筋を支配する。",
    ),
    "Q1951": (
        "KN1553",
        "心筋細胞の活動電位は複数のイオンチャネルによる内向き・外向き電流の時間的変化で形成される。",
    ),
    "Q1952": (
        "KN1554",
        "血清Na濃度の低下は重症度に応じて神経症状を生じ得るため、意識状態と電解質を合わせて評価する。",
    ),
    "Q1953": (
        "KN1555",
        "歩行速度は一定時間に進む距離で表され、歩行周期の時間・空間パラメータと関係する。",
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
    if (manifest.get("question_count"), manifest.get("last_question_number"), manifest.get("bank_version")) != (1953, 1953, "2026-09-b18"):
        raise ValueError(f"Lot04 formal integration is not complete: {manifest}")
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
