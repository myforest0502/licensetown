from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected source block not found in {path}: {old[:80]!r}")
    file_path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    path = "goukaku_ui.py"
    replace_once(
        path,
        "from field_progress import build_field_progress\n",
        "from field_progress import build_field_progress\nfrom dashboard_real_data_shadow import build_dashboard_real_data_shadow\n",
    )
    replace_once(
        path,
        '''def overall_progress_ui_enabled():\n    return os.getenv("ENABLE_OVERALL_PROGRESS_UI", "").strip().lower() in {\n        "1", "true", "yes", "on",\n    }\n\n\ndef phase12_guidance_preview_enabled():\n''',
        '''def overall_progress_ui_enabled():\n    return os.getenv("ENABLE_OVERALL_PROGRESS_UI", "").strip().lower() in {\n        "1", "true", "yes", "on",\n    }\n\n\ndef dashboard_real_data_shadow_enabled():\n    return os.getenv("ENABLE_DASHBOARD_REAL_DATA_SHADOW", "").strip().lower() in {\n        "1", "true", "yes", "on",\n    }\n\n\ndef phase12_guidance_preview_enabled():\n''',
    )
    replace_once(
        path,
        '''        "overall_progress_ui_enabled": False,\n        "overall_progress_preview": None,\n        "phase12_guidance_preview_enabled": False,\n''',
        '''        "overall_progress_ui_enabled": False,\n        "overall_progress_preview": None,\n        "dashboard_real_data_shadow_enabled": False,\n        "dashboard_real_data_shadow": None,\n        "phase12_guidance_preview_enabled": False,\n''',
    )
    replace_once(
        path,
        '''        field_preview = field_progress_ui_enabled()\n        overall_preview = overall_progress_ui_enabled()\n        phase12_preview = phase12_guidance_preview_enabled()\n        attempts = None\n        evidence = None\n        if field_preview or overall_preview or phase12_preview:\n            attempts = get_question_attempts(user_id)\n            evidence = build_field_evidence(attempts)\n        if field_preview or overall_preview:\n            progress = build_field_progress(evidence)\n''',
        '''        field_preview = field_progress_ui_enabled()\n        overall_preview = overall_progress_ui_enabled()\n        shadow_preview = dashboard_real_data_shadow_enabled()\n        phase12_preview = phase12_guidance_preview_enabled()\n        attempts = None\n        evidence = None\n        progress = None\n        if field_preview or overall_preview or shadow_preview or phase12_preview:\n            attempts = get_question_attempts(user_id)\n            evidence = build_field_evidence(attempts)\n        if field_preview or overall_preview or shadow_preview:\n            progress = build_field_progress(evidence)\n''',
    )
    replace_once(
        path,
        '''        current_guidance = build_learning_guidance(dashboard["total_answers"], fields)\n        dashboard.update(current_guidance)\n        if phase12_preview:\n''',
        '''        current_guidance = build_learning_guidance(dashboard["total_answers"], fields)\n        dashboard.update(current_guidance)\n        if shadow_preview:\n            legacy_recommended_field = (\n                dashboard["recommended_study"][0][0]\n                if dashboard["recommended_study"] else None\n            )\n            dashboard["dashboard_real_data_shadow_enabled"] = True\n            dashboard["dashboard_real_data_shadow"] = build_dashboard_real_data_shadow(\n                attempts,\n                evidence=evidence,\n                progress=progress,\n                legacy_overall_progress_percent=dashboard["overall_progress"],\n                legacy_weak_fields=dashboard["weak_fields"],\n                legacy_recommended_field=legacy_recommended_field,\n            )\n        if phase12_preview:\n''',
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
