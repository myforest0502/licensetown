"""One-command AI reliability shadow runner; never touches production data/state."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alternative_repair_ai_reliability import (
    DEFAULT_MODEL,
    build_evaluator_messages,
    build_not_run_plan,
    run_shadow_validation,
)


DEFAULT_OUTPUT = ROOT / "data" / "question_bank" / "alternative_repair_ai_shadow_result_v0.1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    if args.plan_only or not os.environ.get("OPENAI_API_KEY"):
        report = build_not_run_plan(
            "plan_only" if args.plan_only else "not_run_api_credentials_unavailable"
        )
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"status={report['status']} planned_api_calls={report['planned_api_calls']}")
        return 0 if args.plan_only else 2

    from openai import OpenAI

    client = OpenAI()

    def evaluator(packet, answer):
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=build_evaluator_messages(packet, answer),
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=500,
        )
        return json.loads(response.choices[0].message.content or "{}")

    report = run_shadow_validation(evaluator)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"status=completed calls={report['actual_api_calls']} "
        f"false_pass={report['false_pass_count']} instability={report['verdict_instability_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
