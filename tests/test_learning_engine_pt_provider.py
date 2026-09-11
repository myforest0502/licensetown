"""Regression coverage for the learning-engine-only PT provider connection."""

from datetime import datetime, timezone
from pathlib import Path
import random
import subprocess
import sys

import pytest

import learning_engine as engine
import question_bank
from qualifications.pt.provider import PTQuestionBankProvider


BANK_METHODS = ("question_ids", "get_question", "get_question_tag", "get_quiz_question")
NOW = datetime(2026, 9, 11, tzinfo=timezone.utc)


def test_bank_access_uses_one_pt_provider_and_formal_ids():
    assert isinstance(engine._PT_BANK, PTQuestionBankProvider)
    assert engine._PT_BANK.qualification_id == "pt"
    for name in BANK_METHODS:
        assert getattr(engine, name).__self__ is engine._PT_BANK
        assert getattr(engine, name).__func__ is getattr(PTQuestionBankProvider, name)
    assert engine.question_ids() == question_bank.question_ids()


@pytest.mark.parametrize("name", BANK_METHODS)
def test_engine_bank_access_preserves_arguments_and_result(monkeypatch, name):
    args = () if name == "question_ids" else (" q1 ",)
    result = ("Q2", "Q1") if not args else {"raw": [" unchanged "]}
    calls = []

    def bank_read(*received):
        calls.append(received)
        return result

    monkeypatch.setattr(question_bank, name, bank_read)
    assert getattr(engine, name)(*args) is result
    assert calls == [args]


@pytest.mark.parametrize("kind,category", [("initial", None), ("daily", None), ("daily", 18)])
def test_sessions_match_direct_bank_output(monkeypatch, kind, category):
    history = [{
        "question_id": "Q1411", "is_correct": False, "confidence": 1,
        "answered_at": NOW,
    }]

    def build():
        if kind == "initial":
            return engine.build_initial_assessment(
                10, exclude_ids={"Q972"}, rng=random.Random(314)
            )
        return engine.build_daily_session(
            history, category_small=category, exclude_ids={"Q972"},
            rng=random.Random(314), as_of=NOW,
        )

    through_provider = build()
    # Recreate the pre-connection access path without copying selection logic.
    with monkeypatch.context() as direct:
        for name in BANK_METHODS:
            direct.setattr(engine, name, getattr(question_bank, name))
        assert through_provider == build()
    assert len(through_provider) == (10 if kind == "initial" else 30)
    for question in through_provider:
        assert question == question_bank.get_quiz_question(question["id"])
        assert question["id"] not in {"Q972", "Q1354"}
        if kind == "daily":
            assert question["id"] not in {"Q1411", "Q1585"}
        if category is not None:
            assert int(question["category_small"]) == category


@pytest.mark.parametrize("kwargs", [{"category_small": 14}, {"exclude_ids": question_bank.question_ids()}])
def test_daily_availability_error_type_and_condition_are_preserved(kwargs):
    assert engine.QuestionAvailabilityError is question_bank.QuestionAvailabilityError
    with pytest.raises(question_bank.QuestionAvailabilityError,
                       match="Not enough non-blocked questions for daily session"):
        engine.build_daily_session([], as_of=NOW, **kwargs)


def test_daily_session_still_prioritizes_safety(monkeypatch):
    ids_by_safety = {}
    for q_id in engine.question_ids():
        ids_by_safety.setdefault(engine.get_question_tag(q_id).get("safety"), q_id)
    critical = ids_by_safety["critical"]
    ordinary = ids_by_safety["none"]
    monkeypatch.setattr(engine, "question_ids", lambda: (ordinary, critical))
    selected = engine.build_daily_session([], question_count=1, rng=random.Random(314), as_of=NOW)
    assert selected == [question_bank.get_quiz_question(critical)]


def test_fresh_engine_import_does_not_depend_on_app_or_database():
    script = r'''
import importlib.abc
import sys

blocked = {"app", "wsgi", "database", "psycopg", "psycopg2",
           "sqlite3", "openai", "linebot"}

class BlockRuntimeImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in blocked:
            raise AssertionError("Runtime/DB import: " + fullname)

def audit(event, args):
    if event.startswith(("socket.", "subprocess.", "sqlite3.")):
        raise AssertionError("External side effect: " + event)

sys.meta_path.insert(0, BlockRuntimeImports())
sys.addaudithook(audit)
import learning_engine
assert learning_engine.question_ids()
assert not blocked.intersection(sys.modules)
'''
    result = subprocess.run(
        [sys.executable, "-B", "-c", script],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
