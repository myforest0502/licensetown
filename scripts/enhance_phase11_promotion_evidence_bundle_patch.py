from pathlib import Path

path = Path("pilot_diagnostics.py")
text = path.read_text(encoding="utf-8")

old = '''    lines = [\n        "PHASE11_PROMOTION_EVIDENCE_V1",'''
new = '''    shadow_evidence = " | ".join(str(item) for item in (shadow.get("evidence") or [])) or "none"\n    shadow_observations = " | ".join(str(item) for item in (shadow.get("observations") or [])) or "none"\n\n    lines = [\n        "PHASE11_PROMOTION_EVIDENCE_V1",'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"shadow evidence insertion target count={text.count(old)}")
    text = text.replace(old, new)

old = '''        f"shadow_confidence={shadow.get('confidence') or 'none'}",\n        f"comparison_label={comparison.get('label') or 'none'}",'''
new = '''        f"shadow_confidence={shadow.get('confidence') or 'none'}",\n        f"shadow_evidence={shadow_evidence}",\n        f"shadow_observations={shadow_observations}",\n        f"comparison_label={comparison.get('label') or 'none'}",'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"shadow lines target count={text.count(old)}")
    text = text.replace(old, new)

old = '''    ]\n    return "\\n".join(lines)\n\n\ndef build_pilot_diagnostics'''
new = '''    ]\n    for index, snapshot in enumerate(replay.get("snapshots") or [], start=1):\n        eligible = bool(snapshot.get("eligible"))\n        issues = " | ".join(str(item) for item in (snapshot.get("coverage_issues") or [])) or "none"\n        lines.append(\n            "replay_snapshot_" + str(index) + "=" + ",".join([\n                f"at:{snapshot.get('snapshot_jst') or snapshot.get('snapshot_at') or 'none'}",\n                f"eligible:{str(eligible).lower()}",\n                f"coverage:{snapshot.get('coverage_status') or 'none'}",\n                f"baseline:{snapshot.get('baseline_target') or 'none'}",\n                f"baseline_goal:{snapshot.get('baseline_goal') if snapshot.get('baseline_goal') is not None else 'none'}",\n                f"baseline_phase:{snapshot.get('baseline_phase') or 'none'}",\n                f"shadow:{snapshot.get('shadow_target') or 'none'}",\n                f"shadow_reason:{snapshot.get('shadow_reason_code') or 'none'}",\n                f"comparison:{snapshot.get('comparison_label') or 'none'}",\n                f"review:{snapshot.get('review_category') or 'none'}",\n                f"profile_consistent:{str(bool(snapshot.get('shadow_reason_profile_consistent'))).lower() if eligible else 'none'}",\n                f"phase11_safety_miss:{str(bool(snapshot.get('phase11_critical_safety_miss_candidate') or snapshot.get('critical_safety_miss_candidate'))).lower()}",\n                f"baseline_safety_miss:{str(bool(snapshot.get('baseline_stronger_safety_miss_candidate'))).lower()}",\n                f"j2_j3_trigger_mismatch:{str(bool(snapshot.get('ordinary_single_wrong_takeover_candidate'))).lower()}",\n                f"coverage_issues:{issues}",\n            ])\n        )\n    return "\\n".join(lines)\n\n\ndef build_pilot_diagnostics'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"snapshot insertion target count={text.count(old)}")
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
