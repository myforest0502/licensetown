from pathlib import Path


def replace_once(path, old, new):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"missing expected test block in {path}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def main():
    replace_once(
        "tests/test_goukaku_ui.py",
        '''        lambda user_id: dashboard,\n''',
        '''        lambda user_id, **kwargs: dashboard,\n''',
    )
    replace_once(
        "tests/test_supporter_activity_phase2.py",
        '''    monkeypatch.setattr(goukaku_ui_module, "build_dashboard", lambda user_id: dashboard)\n''',
        '''    monkeypatch.setattr(goukaku_ui_module, "build_dashboard", lambda user_id, **kwargs: dashboard)\n''',
    )
    replace_once(
        "tests/test_overall_progress_ui.py",
        '''    token = create_dashboard_token("overall-flag-off")\n    text = app.test_client().get(f"/goukaku-no-michi?token={token}").get_data(as_text=True)\n    assert "総合到達度" in text\n''',
        '''    # The legacy preview flags remain off and direct dashboard construction still\n    # avoids the attempt ledger. The authenticated learner route now intentionally\n    # reads attempts for the always-on learner navigation layer.\n    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda *_: [])\n    token = create_dashboard_token("overall-flag-off")\n    text = app.test_client().get(f"/goukaku-no-michi?token={token}").get_data(as_text=True)\n    assert "総合到達度" in text\n''',
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
