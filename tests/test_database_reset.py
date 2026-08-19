"""ユーザープロフィール完全リセットのDB動作を検証する。"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path
from typing import Any


DATABASE_PATH = Path(__file__).resolve().parents[1] / "database.py"


def load_database_code(available, get_connection) -> dict:
    module = ast.parse(
        DATABASE_PATH.read_text(encoding="utf-8"),
        filename=str(DATABASE_PATH),
    )
    targets = {"PersistentUserStore", "reset_user_profile", "user_profile_exists"}
    nodes = [
        node
        for node in module.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef))
        and node.name in targets
    ]
    namespace = {
        "Any": Any,
        "database_is_available": available,
        "get_db_connection": get_connection,
        "_known_user_ids": set(),
        "_local_learning_events": {},
        "_local_learning_seconds": {},
        "_local_learning_time_events": [],
        "_local_supporter_links": {},
    }
    extracted = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(extracted)
    exec(compile(extracted, str(DATABASE_PATH), "exec"), namespace)
    store_class = namespace["PersistentUserStore"]
    namespace["user_names"] = store_class("name")
    namespace["user_modes"] = store_class("mode")
    return namespace


class FakeDatabase:
    def __init__(self, name: str, mode: str, fail_delete: bool = False):
        self.profiles = {
            "user-1": {"name": name, "mode": mode},
            "user-2": {"name": "別ユーザー", "mode": "chat"},
        }
        self.fail_delete = fail_delete
        self.connection_count = 0
        self.delete_count = 0
        self.deleted_learning_tables = []

    def connect(self):
        self.connection_count += 1
        return FakeConnection(self)


class FakeConnection:
    def __init__(self, database: FakeDatabase):
        self.database = database

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def cursor(self):
        return FakeCursor(self.database)


class FakeCursor:
    def __init__(self, database: FakeDatabase):
        self.database = database
        self.selected_row = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query, params):
        normalized = " ".join(query.split())
        user_id = params[0]
        profile = self.database.profiles.get(user_id)

        if normalized.startswith("SELECT name"):
            self.selected_row = None if profile is None else (profile["name"],)
            return

        if normalized.startswith("SELECT mode"):
            self.selected_row = None if profile is None else (profile["mode"],)
            return

        if normalized.startswith("SELECT 1 FROM user_profiles"):
            self.selected_row = None if profile is None else (1,)
            return

        if normalized.startswith("DELETE FROM user_profiles"):
            self.database.delete_count += 1
            if self.database.fail_delete:
                raise RuntimeError("database delete failed")
            self.database.profiles.pop(user_id, None)
            return

        if normalized.startswith("DELETE FROM learning_events"):
            self.database.deleted_learning_tables.append("learning_events")
            return

        if normalized.startswith("DELETE FROM learning_time_totals"):
            self.database.deleted_learning_tables.append("learning_time_totals")
            return

        if normalized.startswith("DELETE FROM learning_time_events"):
            self.database.deleted_learning_tables.append("learning_time_events")
            return

        if normalized.startswith("DELETE FROM supporter_links"):
            self.database.deleted_learning_tables.append("supporter_links")
            return

        raise AssertionError(f"Unexpected SQL: {normalized}")

    def fetchone(self):
        return self.selected_row


class DatabaseResetTest(unittest.TestCase):
    def test_local_reset_clears_name_and_mode(self) -> None:
        namespace = load_database_code(
            available=lambda: False,
            get_connection=lambda: None,
        )
        namespace["user_names"]["user-1"] = "利用者"
        namespace["user_modes"]["user-1"] = "study"

        namespace["reset_user_profile"]("user-1")

        self.assertIsNone(namespace["user_names"].get("user-1"))
        self.assertIsNone(namespace["user_modes"].get("user-1"))
        self.assertFalse(namespace["user_profile_exists"]("user-1"))

    def test_neon_reset_deletes_only_the_target_user_profile(self) -> None:
        database = FakeDatabase(name="利用者", mode="study")
        namespace = load_database_code(
            available=lambda: True,
            get_connection=database.connect,
        )

        namespace["reset_user_profile"]("user-1")

        self.assertEqual(1, database.connection_count)
        self.assertEqual(1, database.delete_count)
        self.assertEqual(
            ["learning_events", "learning_time_totals", "learning_time_events"],
            database.deleted_learning_tables,
        )
        self.assertNotIn("supporter_links", database.deleted_learning_tables)
        self.assertNotIn("user-1", database.profiles)
        self.assertEqual(
            {"name": "別ユーザー", "mode": "chat"},
            database.profiles["user-2"],
        )
        # Render再起動後もプロフィール行が存在せず、完全な初回扱いになる。
        self.assertIsNone(namespace["user_names"].get("user-1"))
        self.assertIsNone(namespace["user_modes"].get("user-1"))
        self.assertFalse(namespace["user_profile_exists"]("user-1"))

    def test_failed_neon_reset_keeps_the_profile_unchanged(self) -> None:
        database = FakeDatabase(
            name="利用者",
            mode="study",
            fail_delete=True,
        )
        namespace = load_database_code(
            available=lambda: True,
            get_connection=database.connect,
        )

        with self.assertRaisesRegex(RuntimeError, "database delete failed"):
            namespace["reset_user_profile"]("user-1")

        self.assertEqual(1, database.delete_count)
        self.assertEqual(
            {"name": "利用者", "mode": "study"},
            database.profiles["user-1"],
        )


if __name__ == "__main__":
    unittest.main()
