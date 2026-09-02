from pathlib import Path

path = Path("phase11_retrospective_shadow_audit.py")
text = path.read_text(encoding="utf-8")

marker = '''\n\ndef build_retrospective_shadow_audit(\n'''
helper = '''\n\ndef _ordinary_single_wrong_takeover_candidate(\n    shadow: dict[str, Any],\n    shadow_profile: dict[str, Any] | None,\n) -> bool:\n    """Flag only a J2/J3 decision whose own formal trigger is absent."""\n    profile = shadow_profile or {}\n    reason = str(shadow.get("reason_code") or "")\n    if reason == "confident_wrong_cluster":\n        supported = (\n            int(profile.get("active_cross_question_confident_wrong_node_count") or 0) >= 1\n            or int(profile.get("active_confident_wrong_repairing_node_count") or 0) >= 2\n        )\n        return not supported\n    if reason == "repeated_wrong_cluster":\n        supported = (\n            int(profile.get("active_cross_question_wrong_node_count") or 0) >= 1\n            or int(profile.get("active_repeated_weakness_node_count") or 0) >= 2\n        )\n        return not supported\n    return False\n'''
if helper not in text:
    if text.count(marker) != 1:
        raise SystemExit(f"helper marker count={text.count(marker)}")
    text = text.replace(marker, helper + marker)

old = '''        ordinary_single_wrong_takeover = bool(\n            shadow.get("reason_code") in {"confident_wrong_cluster", "repeated_wrong_cluster"}\n            and comparison.get("shadow_target_formal_evidence", {}).get("active_repeated_weakness_node_count", 0) == 0\n            and comparison.get("shadow_target_formal_evidence", {}).get("active_cross_question_wrong_node_count", 0) == 0\n        )'''
new = '''        ordinary_single_wrong_takeover = _ordinary_single_wrong_takeover_candidate(\n            shadow, comparison.get("shadow_target_formal_evidence")\n        )'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"takeover target count={text.count(old)}")
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")

path = Path("templates/goukaku/supporter_pilot_diagnostics.html")
text = path.read_text(encoding="utf-8")
old = '''ordinary single-wrong takeover候補 {{ replay.ordinary_single_wrong_takeover_candidate_count }}'''
new = '''J2/J3 formal trigger不整合候補 {{ replay.ordinary_single_wrong_takeover_candidate_count }}'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"template target count={text.count(old)}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
