"""Build concise relation review and AI plan artifacts for boss + Aoi."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alternative_repair_ai_reliability import build_not_run_plan
from alternative_repair_confirmation_shadow import build_relation_review_packets


SUMMARY = ROOT / "data" / "question_bank" / "alternative_repair_human_review_summary_v0.1.md"
RESULT = ROOT / "data" / "question_bank" / "alternative_repair_ai_shadow_result_v0.1.json"


def _short(value, limit=500):
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[:limit] + "…"


def main() -> int:
    lines = ["# ⑩-D Alternative Repair Human Review v0.1", ""]
    for index, packet in enumerate(build_relation_review_packets(), start=1):
        source = packet["source_question"]
        lines.extend([
            f"## {index}. {packet['repair_target_node_id']}",
            f"- Target label: {' / '.join(packet['repair_target_labels'])}",
            f"- Problem A ({source['question_id']}): {_short(source['question_text'])}",
            f"- Answer / explanation A: {source['display_answer']} / {_short(source['explanation'])}",
            f"- A metadata: task={source['task']}, primary={source['primary_ability']}, secondary={source['secondary_ability']}, safety={source['safety']}",
        ])
        for candidate in packet["candidate_confirmations"]:
            for question in candidate["candidate_questions"]:
                lines.extend([
                    f"- Problem B ({question['question_id']}, {candidate['relation_type']}): {_short(question['question_text'])}",
                    f"- Answer / explanation B: {question['display_answer']} / {_short(question['explanation'])}",
                    f"- B metadata: task={question['task']}, primary={question['primary_ability']}, secondary={question['secondary_ability']}, safety={question['safety']}",
                    f"- Relation reason: {_short(candidate['why_it_may_confirm'])}",
                    f"- Risk: {_short(candidate['false_positive_concern'])}",
                ])
        lines.extend([
            "- Codex recommendation: UNCERTAIN (false-positive prevention; no auto-accept)",
            "- Human final decision: [ ] ACCEPT  [ ] REJECT  [ ] UNCERTAIN",
            "",
        ])
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    RESULT.write_text(json.dumps(build_not_run_plan(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(SUMMARY)
    print(RESULT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
