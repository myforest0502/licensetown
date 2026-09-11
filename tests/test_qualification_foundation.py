"""Standalone tests: never import the application or its database module."""

from dataclasses import FrozenInstanceError
from pathlib import Path
import subprocess
import sys
import unittest

from qualifications import (
    DEFAULT_QUALIFICATION_ID,
    QUALIFICATIONS,
    get_default_qualification,
    get_qualification,
)


class QualificationFoundationTest(unittest.TestCase):
    def test_ids_are_unique_and_include_pt_and_takken(self):
        ids = [item.qualification_id for item in QUALIFICATIONS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({"pt", "takken"}.issubset(ids))

    def test_display_names(self):
        self.assertEqual(get_qualification("pt").display_name, "理学療法士")
        self.assertEqual(get_qualification("takken").display_name, "宅地建物取引士")

    def test_default_is_pt(self):
        self.assertEqual(DEFAULT_QUALIFICATION_ID, "pt")
        self.assertIs(get_default_qualification(), get_qualification("pt"))

    def test_unknown_id_does_not_fall_back(self):
        with self.assertRaises(KeyError):
            get_qualification("unknown")

    def test_config_is_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            get_default_qualification().display_name = "changed"

    def test_fresh_import_has_no_db_network_or_write_side_effects(self):
        # A fresh interpreter prevents cached imports from hiding side effects.
        # -B disables Python bytecode writes without changing environment vars.
        script = r'''
import importlib.abc
import os
import sys

blocked = {"app", "wsgi", "database", "question_bank", "psycopg",
           "psycopg2", "sqlite3", "openai", "linebot"}

class BlockRuntimeImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in blocked:
            raise AssertionError("Runtime/DB import: " + fullname)

def audit(event, args):
    if event == "open":
        _, mode, flags = args
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
        if (mode and any(c in mode for c in "wax+")) or (flags & write_flags):
            raise AssertionError("File write during import")
    if event.startswith(("socket.", "subprocess.", "sqlite3.")) or event in {
        "os.system", "os.mkdir", "os.remove", "os.rmdir", "os.rename",
        "os.link", "os.symlink", "os.truncate", "os.chmod", "os.utime",
    }:
        raise AssertionError("Side effect during import: " + event)

sys.meta_path.insert(0, BlockRuntimeImports())
sys.addaudithook(audit)
import qualifications
import qualifications.base
import qualifications.pt.config
import qualifications.takken.config
assert qualifications.get_default_qualification().qualification_id == "pt"
assert not blocked.intersection(sys.modules)
'''
        result = subprocess.run(
            [sys.executable, "-B", "-c", script],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
