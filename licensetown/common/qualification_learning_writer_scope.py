"""Production composition hook for qualification-explicit PT learning writes.

The legacy learner app and dashboard import write helpers by value from
``database``. This installer rebinds only those module-local write hooks to the
PT-qualified writer after the qualified database conflict keys are available.
"""

from __future__ import annotations

from qualifications.pt.learning_writer import PTLearningWriter


_LEGACY_WRITE_NAMES = (
    "record_learning_batch",
    "record_activity_event",
)


def install_pt_learning_writer_scope(legacy_module, dashboard_module) -> None:
    """Bind current PT write call sites to one explicit PT writer instance."""
    if getattr(legacy_module, "_pt_learning_writer_scope_installed", False):
        return

    for name in _LEGACY_WRITE_NAMES:
        if not hasattr(legacy_module, name):
            raise AttributeError(f"legacy learner runtime missing write hook: {name}")
    if not hasattr(dashboard_module, "record_activity_event"):
        raise AttributeError("dashboard runtime missing write hook: record_activity_event")

    writer = PTLearningWriter()
    legacy_module.record_learning_batch = writer.record_learning_batch
    legacy_module.record_activity_event = writer.record_activity_event
    dashboard_module.record_activity_event = writer.record_activity_event
    legacy_module._pt_learning_writer = writer
    legacy_module._pt_learning_writer_scope_installed = True
