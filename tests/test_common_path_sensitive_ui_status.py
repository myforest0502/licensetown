"""Path-sensitive shared UI/status modules keep canonical paths and legacy identity."""

import importlib


def test_developer_status_legacy_alias_uses_pt_canonical_data():
    legacy = importlib.import_module("developer_status")
    canonical = importlib.import_module("licensetown.common.developer_status")
    assert legacy is canonical
    assert "licensetown/pt/data/question_bank" in canonical.BANK_DIR.as_posix()


def test_site_ui_legacy_alias_keeps_repo_previews_and_pt_bank():
    legacy = importlib.import_module("site_ui")
    canonical = importlib.import_module("licensetown.common.site_ui")
    assert legacy is canonical
    assert canonical.PREVIEW_PC_DIR.name == "preview-pc"
    assert canonical.PREVIEW_724_DIR.name == "preview-724"
    assert "licensetown/pt/data/question_bank/questions.json" in canonical.QUESTION_BANK_PATH.as_posix()
