from pathlib import Path

path = Path("judgment_shadow.py")
text = path.read_text(encoding="utf-8")
old = '''    item.setdefault("answered_count", int(item.get("raw_answer_count") or 0))\n    item.setdefault("accuracy", item.get("raw_accuracy"))\n    return item'''
new = '''    item.setdefault("answered_count", int(item.get("raw_answer_count") or 0))\n    item.setdefault("accuracy", item.get("raw_accuracy"))\n    accuracy = item.get("accuracy")\n    item.setdefault(\n        "accuracy_percent",\n        round(float(accuracy) * 100, 1) if accuracy is not None else None,\n    )\n    return item'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"judgment target count={text.count(old)}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")

path = Path("templates/goukaku/supporter_pilot_diagnostics.html")
text = path.read_text(encoding="utf-8")
old = '''正答率 {{ profile.accuracy if profile.accuracy is not none else 'なし' }} / Node coverage'''
new = '''正答率 {{ (profile.accuracy_percent ~ '%') if profile.accuracy_percent is not none else 'なし' }} / Node coverage'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"template target count={text.count(old)}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
