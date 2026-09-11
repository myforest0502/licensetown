"""PT adapter parity and import-isolation tests."""

from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import question_bank
from qualifications.bank_provider import QuestionBankProvider
from qualifications.pt.provider import PTQuestionBankProvider


class PTQuestionBankProviderTest(unittest.TestCase):
    def setUp(self):
        self.provider: QuestionBankProvider = PTQuestionBankProvider()

    def test_provider_satisfies_contract_shape(self):
        # The contract is a structural Protocol, not runtime_checkable.
        self.assertIsInstance(self.provider.qualification_id, str)
        self.assertIsInstance(self.provider.question_ids(), tuple)
        self.assertIsInstance(self.provider.get_question("Q1"), dict)
        self.assertIsInstance(self.provider.get_question_tag("Q1"), dict)
        self.assertIsInstance(self.provider.get_quiz_question("Q1"), dict)

    def test_qualification_id_is_pt(self):
        self.assertEqual(self.provider.qualification_id, "pt")

    def test_question_ids_match_formal_bank(self):
        self.assertEqual(self.provider.question_ids(), question_bank.question_ids())

    def test_representative_questions_match_formal_bank(self):
        for q_id in ("Q1", "Q1000", "Q2000"):
            for name in ("get_question", "get_question_tag", "get_quiz_question"):
                with self.subTest(q_id=q_id, method=name):
                    self.assertEqual(
                        getattr(self.provider, name)(q_id),
                        getattr(question_bank, name)(q_id),
                    )

    def test_forwards_arguments_and_returns_same_object(self):
        # Noncanonical input must also reach the bank without adapter processing.
        for name, args, result in (
            ("question_ids", (), ("Q2", "Q1")),
            ("get_question", (" q1 ",), {"raw": [" unchanged "]}),
            ("get_question_tag", (" q1 ",), {"raw": [" unchanged "]}),
            ("get_quiz_question", (" q1 ",), {"raw": [" unchanged "]}),
        ):
            with self.subTest(method=name):
                with patch.object(question_bank, name, return_value=result) as forward:
                    self.assertIs(getattr(self.provider, name)(*args), result)
                    forward.assert_called_once_with(*args)

    def test_unknown_question_errors_match_formal_bank(self):
        for name in ("get_question", "get_question_tag", "get_quiz_question"):
            with self.subTest(method=name):
                with self.assertRaises(question_bank.QuestionBankError) as original:
                    getattr(question_bank, name)("Q999999")
                with self.assertRaises(type(original.exception)) as adapted:
                    getattr(self.provider, name)("Q999999")
                self.assertEqual(adapted.exception.args, original.exception.args)
                with patch.object(question_bank, name, side_effect=original.exception):
                    with self.assertRaises(type(original.exception)) as forwarded:
                        getattr(self.provider, name)("Q999999")
                    self.assertIs(forwarded.exception, original.exception)

    def test_fresh_import_has_no_runtime_db_network_or_write_effects(self):
        # Formal bank reads are allowed; cached imports must not hide dependencies.
        script = r'''
import importlib.abc
import os
import sys

blocked = {"app", "wsgi", "database", "psycopg", "psycopg2",
           "sqlite3", "openai", "linebot"}

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
from qualifications.pt.provider import PTQuestionBankProvider
assert PTQuestionBankProvider().qualification_id == "pt"
assert PTQuestionBankProvider().question_ids()
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
