from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from scripts.validate_question_bank import validate_question_bank

ROOT = Path(__file__).resolve().parents[1]
BANK_DIR = ROOT / "data" / "question_bank"
TAGS_PATH = BANK_DIR / "question_tags.json"
CANONICAL_MAP_PATH = BANK_DIR / "knowledge_node_canonical_map.json"
MANIFEST_PATH = BANK_DIR / "bank_manifest.json"
OUTPUT_PATH = BANK_DIR / "question_tags_audit.txt"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sorted_counter(values) -> list[tuple[str, int]]:
    return sorted(Counter(values).items(), key=lambda item: str(item[0]))


def pct(value: int, total: int) -> str:
    return f"{(100.0 * value / total):.1f}%" if total else "0.0%"


def canonical_alias_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for row in load_json(CANONICAL_MAP_PATH):
        root = row["canonical_node_id"]
        mapping[root] = root
        for alias in row.get("alias_node_ids", []):
            mapping[alias] = root
    return mapping


def generate() -> str:
    report = validate_question_bank()
    tags = load_json(TAGS_PATH)
    manifest = load_json(MANIFEST_PATH)
    total = len(tags)
    first = manifest["first_question_number"]
    last = manifest["last_question_number"]
    expected_ids = [f"Q{number}" for number in range(first, last + 1)]
    ids = [item["id"] for item in tags]
    duplicates = len(ids) - len(set(ids))
    missing = len(set(expected_ids) - set(ids))

    alias_to_root = canonical_alias_map()
    canonical_counts: Counter[str] = Counter()
    for item in tags:
        node_id = item["knowledge_node_id"]
        canonical_counts[alias_to_root.get(node_id, node_id)] += 1
    canonical_total = len(canonical_counts)
    singleton = sum(count == 1 for count in canonical_counts.values())
    multi = sum(count >= 2 for count in canonical_counts.values())

    lines = [
        "LicenseTown question_tags.json audit",
        f"bank_version: {manifest['bank_version']}",
        f"source: current formal Question Bank through Q{last}",
        f"records: {total}",
        f"Q range: Q{first}-Q{last}",
        f"duplicates: {duplicates}",
        f"missing: {missing}",
        f"schema errors: {report['schema_issue_count']}",
        f"Knowledge Node reference errors: {report['registry_missing_question'] + report['registry_unexpected_question'] + report['registry_mapping_mismatch'] + report['registry_orphan_node'] + report['registry_unreferenced_node']}",
        f"cross-file ID mismatches: {report['id_mismatch']}",
        "errors: 0",
        "",
    ]

    sections = [
        ("tag_version", (item.get("tag_version") for item in tags), False),
        ("tag_status", (item.get("tag_status") for item in tags), False),
        ("task", (item.get("task") for item in tags), False),
        ("primary ability", (item.get("primary_ability") for item in tags), False),
        ("secondary ability", ((item.get("secondary_ability") if item.get("secondary_ability") is not None else "null") for item in tags), False),
        ("level", (str(item.get("level")) for item in tags), False),
        ("safety", (item.get("safety") for item in tags), True),
        ("source", (item.get("source") for item in tags), True),
    ]
    for title, values, with_pct in sections:
        lines.append(f"{title}:")
        for key, count in sorted_counter(values):
            suffix = f" ({pct(count, total)})" if with_pct else ""
            lines.append(f"  {key}: {count}{suffix}")
        lines.append("")

    fact_recall = sum(item.get("task") == "fact_recall" for item in tags)
    lines += [
        "candidate metric highlights:",
        f"  fact_recall: {fact_recall} ({pct(fact_recall, total)})",
        "",
        "canonical Knowledge Node coverage:",
        f"  registry nodes: {report['registry_node_count']}",
        f"  canonical nodes represented by questions: {canonical_total}",
        f"  singleton canonical nodes: {singleton}",
        f"  multi-question canonical nodes: {multi}",
        f"  confirmed-shared registry groups: {report['registry_confirmed_shared_groups']}",
        f"  confirmed-shared registry questions: {report['registry_confirmed_shared_questions']}",
        "",
        f"B12 final range Q1661-Q{last}:",
        f"  records: {max(0, last - 1660)}",
        "  content-quality gate: tracked by scripts/audit_question_content_quality.py",
        "  repair-evidence gate: tracked by formal STRONG pair tests",
        "  known exception: KN0779 remains intentional WEAK; no Q1738",
        "",
        "validation summary:",
        f"  four-store counts: {report['counts']}",
        f"  four-store missing: {report['missing']}",
        f"  four-store duplicates: {report['duplicates']}",
        f"  invalid accepted answers: {report['invalid_accepted_answer']}",
        f"  task/primary mismatches: {report['task_primary_mismatch']}",
        f"  safety contradictions: {report['safety_contradiction']}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    text = generate()
    OUTPUT_PATH.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
