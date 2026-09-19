"""Prevent qualification-domain code from drifting back to repository root."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = ROOT / "licensetown"
RUNTIME_ROOT_EXCEPTIONS = {"app.py", "database.py", "wsgi.py"}


def test_only_three_canonical_domain_directories_exist():
    dirs = {
        path.name
        for path in DOMAIN_ROOT.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    }
    assert dirs == {"common", "pt", "takken"}


def test_top_level_python_modules_have_domain_home_or_are_runtime_bridges():
    canonical_names = set()
    for domain in ("common", "pt", "takken"):
        canonical_names.update(
            path.name
            for path in (DOMAIN_ROOT / domain).glob("*.py")
        )

    root_python = {
        path.name
        for path in ROOT.glob("*.py")
    }
    unowned = root_python - canonical_names - RUNTIME_ROOT_EXCEPTIONS
    assert unowned == set()


def test_pt_question_bank_data_has_one_canonical_home():
    legacy_root = ROOT / "data"
    canonical_bank = DOMAIN_ROOT / "pt" / "data" / "question_bank"
    assert not legacy_root.exists()
    assert (canonical_bank / "questions.json").exists()
    assert (canonical_bank / "answers.json").exists()
    assert (canonical_bank / "explanations.json").exists()
    assert (canonical_bank / "question_tags.json").exists()
