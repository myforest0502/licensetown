"""Canonical LicenseTown three-folder qualification layout."""

import importlib
from pathlib import Path

def test_licensetown_has_exactly_three_domain_directories():
    package_root = Path(__file__).resolve().parents[1] / "licensetown"
    dirs = {
        p.name for p in package_root.iterdir()
        if p.is_dir() and p.name != "__pycache__"
    }
    assert dirs == {"common", "pt", "takken"}

def test_legacy_metadata_points_to_canonical_objects():
    legacy = importlib.import_module("qualifications")
    canonical = importlib.import_module("licensetown")
    assert legacy.PT is canonical.PT
    assert legacy.TAKKEN is canonical.TAKKEN

def test_exam_weight_legacy_paths_share_canonical_module():
    root = importlib.import_module("exam_weight_shadow")
    legacy = importlib.import_module("qualifications.pt.exam_weight_shadow")
    canonical = importlib.import_module("licensetown.pt.exam_weight_shadow")
    assert root is legacy is canonical

def test_active_repair_legacy_paths_share_canonical_module():
    root = importlib.import_module("phase11_active_repair_rules")
    legacy = importlib.import_module("qualifications.pt.phase11_active_repair_rules")
    canonical = importlib.import_module("licensetown.pt.phase11_active_repair_rules")
    assert root is legacy is canonical
