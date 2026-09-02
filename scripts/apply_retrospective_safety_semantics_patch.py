from pathlib import Path

path = Path("phase11_retrospective_shadow_audit.py")
text = path.read_text(encoding="utf-8")

marker = '''\n\ndef build_retrospective_shadow_audit(\n'''
helper = '''\n\ndef _safety_miss_flags(\n    shadow: dict[str, Any],\n    field_profiles: dict[str, dict[str, Any]],\n    baseline_target: str | None,\n) -> dict[str, bool]:\n    """Separate Phase11 Safety miss from a weaker Baseline Safety target."""\n    any_critical = any(\n        int(profile.get("critical_safety_unresolved_count") or 0) > 0\n        for profile in field_profiles.values()\n    )\n    shadow_target = str(shadow.get("target_field") or "")\n    shadow_profile = field_profiles.get(shadow_target) or {}\n    baseline_profile = field_profiles.get(str(baseline_target or "")) or {}\n    shadow_critical = int(shadow_profile.get("critical_safety_unresolved_count") or 0)\n    baseline_critical = int(baseline_profile.get("critical_safety_unresolved_count") or 0)\n    phase11_miss = bool(any_critical and shadow.get("reason_code") != "safety_repair")\n    baseline_miss = bool(\n        shadow.get("reason_code") == "safety_repair"\n        and shadow_critical > 0\n        and baseline_target != shadow.get("target_field")\n        and baseline_critical == 0\n    )\n    return {\n        "phase11_critical_safety_miss_candidate": phase11_miss,\n        "baseline_stronger_safety_miss_candidate": baseline_miss,\n    }\n'''
if helper not in text:
    if text.count(marker) != 1:
        raise SystemExit(f"helper marker count={text.count(marker)}")
    text = text.replace(marker, helper + marker)

old = '''        critical_safety_miss = bool(\n            shadow.get("reason_code") == "safety_repair"\n            and anchor["field"] != shadow.get("target_field")\n        )\n        ordinary_single_wrong_takeover = bool('''
new = '''        safety_flags = _safety_miss_flags(shadow, profiles, anchor["field"])\n        critical_safety_miss = safety_flags["phase11_critical_safety_miss_candidate"]\n        baseline_safety_miss = safety_flags["baseline_stronger_safety_miss_candidate"]\n        ordinary_single_wrong_takeover = bool('''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"miss target count={text.count(old)}")
    text = text.replace(old, new)

old = '''        if critical_safety_miss:\n            counts["critical_safety_miss_candidates"] += 1\n        if ordinary_single_wrong_takeover:'''
new = '''        if critical_safety_miss:\n            counts["critical_safety_miss_candidates"] += 1\n        if baseline_safety_miss:\n            counts["baseline_stronger_safety_miss_candidates"] += 1\n        if ordinary_single_wrong_takeover:'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"count target count={text.count(old)}")
    text = text.replace(old, new)

old = '''            "critical_safety_miss_candidate": critical_safety_miss,\n            "ordinary_single_wrong_takeover_candidate": ordinary_single_wrong_takeover,'''
new = '''            "critical_safety_miss_candidate": critical_safety_miss,\n            "phase11_critical_safety_miss_candidate": critical_safety_miss,\n            "baseline_stronger_safety_miss_candidate": baseline_safety_miss,\n            "ordinary_single_wrong_takeover_candidate": ordinary_single_wrong_takeover,'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"snapshot target count={text.count(old)}")
    text = text.replace(old, new)

old = '''        "critical_safety_miss_candidate_count": counts["critical_safety_miss_candidates"],\n        "ordinary_single_wrong_takeover_candidate_count": counts["ordinary_single_wrong_takeover_candidates"],'''
new = '''        "critical_safety_miss_candidate_count": counts["critical_safety_miss_candidates"],\n        "phase11_critical_safety_miss_candidate_count": counts["critical_safety_miss_candidates"],\n        "baseline_stronger_safety_miss_candidate_count": counts["baseline_stronger_safety_miss_candidates"],\n        "ordinary_single_wrong_takeover_candidate_count": counts["ordinary_single_wrong_takeover_candidates"],'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"summary target count={text.count(old)}")
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")

path = Path("templates/goukaku/supporter_pilot_diagnostics.html")
text = path.read_text(encoding="utf-8")
old = '''<p>Critical Safety見逃し候補 {{ replay.critical_safety_miss_candidate_count }} / ordinary single-wrong takeover候補 {{ replay.ordinary_single_wrong_takeover_candidate_count }}</p>'''
new = '''<p>Phase11 Critical Safety見逃し候補 {{ replay.phase11_critical_safety_miss_candidate_count }} / Baseline Safety見逃し候補 {{ replay.baseline_stronger_safety_miss_candidate_count }} / ordinary single-wrong takeover候補 {{ replay.ordinary_single_wrong_takeover_candidate_count }}</p>'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"template target count={text.count(old)}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
