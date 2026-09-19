"""Canonical shared core and PT companion imports."""
import importlib

def test_common_core_aliases():
    for name in ("learning_time_guard","supporter_performance","question_order_quality"):
        assert importlib.import_module(name) is importlib.import_module(f"licensetown.common.{name}")

def test_database_intentionally_remains_at_runtime_root():
    database = importlib.import_module("database")
    assert database.__name__ == "database"

def test_companion_record_is_pt_canonical():
    assert importlib.import_module("companion_record") is importlib.import_module("licensetown.pt.companion_record")
