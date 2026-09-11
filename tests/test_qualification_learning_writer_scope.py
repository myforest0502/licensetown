"""Regression coverage for PT qualification-explicit write composition."""

from types import SimpleNamespace

from qualification_learning_writer_scope import install_pt_learning_writer_scope
from qualifications.pt.learning_writer import PTLearningWriter


def make_legacy():
    return SimpleNamespace(
        record_learning_batch=object(),
        record_activity_event=object(),
    )


def make_dashboard():
    return SimpleNamespace(record_activity_event=object())


def test_installer_binds_legacy_and_dashboard_writes_to_one_pt_writer():
    legacy = make_legacy()
    dashboard = make_dashboard()

    install_pt_learning_writer_scope(legacy, dashboard)

    writer = legacy._pt_learning_writer
    assert isinstance(writer, PTLearningWriter)
    assert writer.qualification_id == "pt"
    assert legacy._pt_learning_writer_scope_installed is True

    assert legacy.record_learning_batch.__self__ is writer
    assert legacy.record_learning_batch.__func__ is PTLearningWriter.record_learning_batch
    assert legacy.record_activity_event.__self__ is writer
    assert legacy.record_activity_event.__func__ is PTLearningWriter.record_activity_event
    assert dashboard.record_activity_event.__self__ is writer
    assert dashboard.record_activity_event.__func__ is PTLearningWriter.record_activity_event


def test_installer_is_idempotent():
    legacy = make_legacy()
    dashboard = make_dashboard()
    install_pt_learning_writer_scope(legacy, dashboard)
    first_writer = legacy._pt_learning_writer
    first_batch_hook = legacy.record_learning_batch
    first_legacy_activity_hook = legacy.record_activity_event
    first_dashboard_activity_hook = dashboard.record_activity_event

    install_pt_learning_writer_scope(legacy, dashboard)

    assert legacy._pt_learning_writer is first_writer
    assert legacy.record_learning_batch == first_batch_hook
    assert legacy.record_activity_event == first_legacy_activity_hook
    assert dashboard.record_activity_event == first_dashboard_activity_hook


def test_installer_fails_closed_before_mutating_when_hook_is_missing():
    legacy = make_legacy()
    dashboard = SimpleNamespace()
    original_batch = legacy.record_learning_batch
    original_activity = legacy.record_activity_event

    try:
        install_pt_learning_writer_scope(legacy, dashboard)
    except AttributeError as exc:
        assert "record_activity_event" in str(exc)
    else:
        raise AssertionError("missing dashboard write hook must fail closed")

    assert legacy.record_learning_batch is original_batch
    assert legacy.record_activity_event is original_activity
    assert not hasattr(legacy, "_pt_learning_writer_scope_installed")
