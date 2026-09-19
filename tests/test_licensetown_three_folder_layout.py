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


def test_metadata_objects_live_in_canonical_package():
    canonical = importlib.import_module("licensetown")
    assert canonical.PT.qualification_id == "pt"
    assert canonical.TAKKEN.qualification_id == "takken"


def test_exam_weight_root_alias_points_to_canonical_module():
    root = importlib.import_module("exam_weight_shadow")
    canonical = importlib.import_module("licensetown.pt.exam_weight_shadow")
    assert root is canonical


def test_active_repair_root_alias_points_to_canonical_module():
    root = importlib.import_module("phase11_active_repair_rules")
    canonical = importlib.import_module("licensetown.pt.phase11_active_repair_rules")
    assert root is canonical
