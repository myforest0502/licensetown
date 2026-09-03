from pathlib import Path


path = Path("tests/test_quiz_answer_numbering.py")
text = path.read_text(encoding="utf-8")
old = '        "parse_dashboard_recommendation_command",\n'
new = '        "parse_dashboard_recommendation_command",\n        "parse_category_route_command",\n'
if old not in text:
    raise RuntimeError("target_names insertion point not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
