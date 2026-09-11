"""Regression coverage for the production PT history-scope composition hook."""

from types import SimpleNamespace

from qualification_history_scope import install_pt_learning_history_scope
from qualifications.pt.learning_store import PTLearningHistoryStore


NAMES = (
    "get_question_attempts",
    "get_question_history",
    "is_initial_assessment_completed",
    "mark_initial_assessment_completed",
)


def make_legacy():
    return SimpleNamespace(**{name: object() for name in NAMES})


def test_installer_binds_all_history_hooks_to_one_pt_store():
    legacy = make_legacy()

    install_pt_learning_history_scope(legacy)

    store = legacy._pt_learning_history_store
    assert isinstance(store, PTLearningHistoryStore)
    assert store.qualification_id == "pt"
    assert legacy._pt_learning_history_scope_installed is True
    for name in NAMES:
        bound = getattr(legacy, name)
        assert bound.__self__ is store
        assert bound.__func__ is getattr(PTLearningHistoryStore, name)


def test_installer_is_idempotent():
    legacy = make_legacy()
    install_pt_learning_history_scope(legacy)
    first_store = legacy._pt_learning_history_store
    first_hooks = {name: getattr(legacy, name) for name in NAMES}

    install_pt_learning_history_scope(legacy)

    assert legacy._pt_learning_history_store is first_store
    assert {name: getattr(legacy, name) for name in NAMES} == first_hooks


def test_installer_fails_if_legacy_runtime_lacks_required_hook():
    legacy = make_legacy()
    delattr(legacy, "get_question_history")

    try:
        install_pt_learning_history_scope(legacy)
    except AttributeError as exc:
        assert "get_question_history" in str(exc)
    else:
        raise AssertionError("missing legacy hook must fail closed")
