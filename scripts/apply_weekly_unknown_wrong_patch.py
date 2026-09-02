from pathlib import Path

path = Path("database.py")
text = path.read_text(encoding="utf-8")
old = '''    attempted = {str(item.get("question_id")) for item in attempts}\n    wrong = {str(item.get("question_id")) for item in attempts if item.get("is_correct") is False}\n    unknown = {str(item.get("question_id")) for item in attempts if item.get("answer_status") == "unknown" or (not item.get("selected_answers") and item.get("confidence") is None)}\n    confident_wrong = {str(item.get("question_id")) for item in attempts if item.get("is_correct") is False and item.get("confidence") == 1 and str(item.get("question_id")) not in unknown}'''
new = '''    def is_unknown_attempt(item):\n        return (\n            item.get("answer_status") == "unknown"\n            or (not item.get("selected_answers") and item.get("confidence") is None)\n        )\n\n    attempted = {str(item.get("question_id")) for item in attempts}\n    wrong = {\n        str(item.get("question_id"))\n        for item in attempts\n        if item.get("is_correct") is False and not is_unknown_attempt(item)\n    }\n    unknown = {\n        str(item.get("question_id"))\n        for item in attempts\n        if is_unknown_attempt(item)\n    }\n    confident_wrong = {\n        str(item.get("question_id"))\n        for item in attempts\n        if item.get("is_correct") is False\n        and item.get("confidence") == 1\n        and not is_unknown_attempt(item)\n    }'''
if new not in text:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"patch target count={count}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
