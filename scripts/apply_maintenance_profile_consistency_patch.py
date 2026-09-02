from pathlib import Path

path = Path("judgment_shadow.py")
text = path.read_text(encoding="utf-8")
old = '''        "shadow_reason_profile_consistent": bool(\n            shadow_profile\n            and shadow_profile.get("strongest_reason_code") == shadow.get("reason_code")\n        ),'''
new = '''        "shadow_reason_profile_consistent": bool(\n            (\n                shadow.get("reason_code") == "maintenance_only"\n                and shadow_target is None\n            )\n            or (\n                shadow_profile\n                and shadow_profile.get("strongest_reason_code") == shadow.get("reason_code")\n            )\n        ),'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"target count={text.count(old)}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
