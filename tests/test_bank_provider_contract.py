"""Standalone tests for the qualification question-bank provider contract."""

from pathlib import Path
import subprocess
import sys
import unittest

from qualifications.bank_provider import QuestionBankProvider


class FakeProvider:
    qualification_id = "fake"

    def question_ids(self) -> tuple[str, ...]:
        return ("Q1",)

    def get_question(self, q_id: str) -> dict:
        return {"id": q_id, "question_text": "fake"}

    def get_question_tag(self, q_id: str) -> dict:
        return {"id": q_id, "primary_ability": "fake"}

    def get_quiz_question(self, q_id: str) -> dict:
        return {"id": q_id, "question": "fake", "choices": {"A": "x"}}


class QuestionBankProviderContractTest(unittest.TestCase):
    def setUp(self):
        self.provider: QuestionBankProvider = FakeProvider()

    def test_fake_provider_satisfies_contract_shape(self):
        self.assertEqual(self.provider.qualification_id, "fake")
        self.assertEqual(self.provider.question_ids(), ("Q1",))
        self.assertEqual(self.provider.get_question("Q1")["id"], "Q1")
        self.assertEqual(self.provider.get_question_tag("Q1")["id"], "Q1")
        self.assertEqual(self.provider.get_quiz_question("Q1")["id"], "Q1")

    def test_contract_import_has_no_runtime_side_effects(self):
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
from qualifications.bank_provider import QuestionBankProvider
assert QuestionBankProvider.__name__ == "QuestionBankProvider"
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
