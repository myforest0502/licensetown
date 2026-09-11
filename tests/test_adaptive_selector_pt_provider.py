"""Regression coverage for the adaptive-selector PT provider connection."""

import random

import adaptive_question_selector as selector
import question_bank
from qualifications.pt.provider import PTQuestionBankProvider


PROVIDER_METHODS = ("question_ids", "get_question_tag", "get_quiz_question")


def test_selector_uses_one_pt_provider_for_supported_bank_reads():
    assert isinstance(selector._PT_BANK, PTQuestionBankProvider)
    assert selector._PT_BANK.qualification_id == "pt"
    for name in PROVIDER_METHODS:
        bound = getattr(selector, name)
        assert bound.__self__ is selector._PT_BANK
        assert bound.__func__ is getattr(PTQuestionBankProvider, name)


def test_category_lookup_stays_on_legacy_bank_for_now():
    assert selector.get_category_small is question_bank.get_category_small


def test_provider_bound_reads_preserve_arguments_and_results(monkeypatch):
    for name, args, result in (
        ("question_ids", (), ("Q2", "Q1")),
        ("get_question_tag", (" q1 ",), {"raw": [" unchanged "]}),
        ("get_quiz_question", (" q1 ",), {"raw": [" unchanged "]}),
    ):
        calls = []

        def bank_read(*received):
            calls.append(received)
            return result

        monkeypatch.setattr(question_bank, name, bank_read)
        assert getattr(selector, name)(*args) is result
        assert calls == [args]


def test_selector_output_matches_direct_legacy_bank_path(monkeypatch):
    def build():
        return selector.select_node_adaptive_questions(
            [], question_count=12, rng=random.Random(314), category_small=18
        )

    through_provider = build()
    with monkeypatch.context() as direct:
        direct.setattr(selector, "question_ids", question_bank.question_ids)
        direct.setattr(selector, "get_question_tag", question_bank.get_question_tag)
        direct.setattr(selector, "get_quiz_question", question_bank.get_quiz_question)
        direct_legacy = build()

    assert through_provider == direct_legacy


def test_built_session_matches_direct_legacy_bank_path(monkeypatch):
    def build():
        return selector.build_node_adaptive_session(
            [], question_count=12, rng=random.Random(314), category_small=18
        )

    through_provider = build()
    with monkeypatch.context() as direct:
        direct.setattr(selector, "question_ids", question_bank.question_ids)
        direct.setattr(selector, "get_question_tag", question_bank.get_question_tag)
        direct.setattr(selector, "get_quiz_question", question_bank.get_quiz_question)
        direct_legacy = build()

    assert through_provider == direct_legacy
