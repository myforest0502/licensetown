from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as bot_app
import database
from site_marketing_refresh import refresh_public_site_html
from site_ui import PREVIEW_724_DIR, PREVIEW_PC_DIR


def _event(user_id, text="学習者"):
    return SimpleNamespace(
        source=SimpleNamespace(user_id=user_id),
        message=SimpleNamespace(text=text),
        reply_token="reply-token",
    )


def setup_function():
    database._local_free_monitor_slots.clear()


def teardown_function():
    database._local_free_monitor_slots.clear()


def test_local_claim_is_idempotent_caps_thirty_and_survives_reset():
    assert database.claim_free_monitor_slot("same-user") == 1
    assert database.claim_free_monitor_slot("same-user") == 1
    for number in range(2, 31):
        assert database.claim_free_monitor_slot(f"user-{number}") == number
    assert database.claim_free_monitor_slot("user-31") is None
    database.reset_user_profile("same-user")
    assert database.claim_free_monitor_slot("same-user") == 1
    assert len(database._local_free_monitor_slots) == 30


def test_local_concurrent_unique_claims_never_exceed_thirty():
    with ThreadPoolExecutor(max_workers=40) as executor:
        results = list(executor.map(database.claim_free_monitor_slot, [f"u-{n}" for n in range(60)]))
    assert sum(result is not None for result in results) == 30
    assert len(database._local_free_monitor_slots) == 30
    assert len(set(database._local_free_monitor_slots.values())) == 30


class ClaimCursor:
    def __init__(self, rows):
        self.rows = iter(rows)
        self.executed = []

    def __enter__(self): return self
    def __exit__(self, *_args): return False
    def execute(self, query, params=None): self.executed.append((" ".join(query.split()), params))
    def fetchone(self): return next(self.rows)


class ClaimConnection:
    def __init__(self, rows): self.cursor_value = ClaimCursor(rows)
    def __enter__(self): return self
    def __exit__(self, *_args): return False
    def cursor(self): return self.cursor_value


def test_database_claim_uses_transaction_lock_and_skip_locked(monkeypatch):
    connection = ClaimConnection([None, (3,)])
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: connection)
    assert database.claim_free_monitor_slot("line-user") == 3
    sql = " ".join(query for query, _params in connection.cursor_value.executed)
    assert "pg_advisory_xact_lock" in sql
    assert "FOR UPDATE SKIP LOCKED" in sql
    assert "UPDATE free_monitor_slots" in sql


def test_schema_initialization_seeds_and_backfills_without_exposing_ids(monkeypatch):
    executed = []

    class Cursor:
        def __enter__(self): return self
        def __exit__(self, *_args): return False
        def execute(self, query, params=None): executed.append((" ".join(query.split()), params))

    class Connection:
        def __enter__(self): return self
        def __exit__(self, *_args): return False
        def cursor(self): return Cursor()

    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: Connection())
    database.init_database()
    sql = " ".join(query for query, _params in executed)
    assert "CREATE TABLE IF NOT EXISTS free_monitor_slots" in sql
    assert "generate_series(1, 30)" in sql
    assert "SELECT user_id FROM learning_events WHERE answered_count > 0" in sql
    assert "SELECT user_id FROM user_profiles WHERE name IS NOT NULL" in sql
    assert "existing free monitor learners exceed capacity" in sql


def test_onboarding_claims_before_name_and_full_capacity_blocks(monkeypatch):
    replies = []
    homes = []
    monkeypatch.setattr(bot_app, "reply_to_line", lambda _token, text: replies.append(text))
    monkeypatch.setattr(bot_app, "reply_mode_select", lambda *_args, **kwargs: homes.append(kwargs))

    accepted = "monitor-accepted"
    bot_app.user_states[accepted] = "waiting_name"
    monkeypatch.setattr(bot_app, "claim_free_monitor_slot", lambda user_id: 1 if user_id == accepted else None)
    bot_app.handle_text_message(_event(accepted))
    assert bot_app.user_names[accepted] == "学習者"
    assert accepted not in bot_app.user_states
    assert len(homes) == 1

    blocked = "monitor-blocked"
    bot_app.user_states[blocked] = "waiting_name"
    bot_app.handle_text_message(_event(blocked))
    assert blocked not in bot_app.user_names
    assert bot_app.user_states[blocked] == "waiting_name"
    assert "無料モニター30名の受付は終了しました" in replies[-1]

    bot_app.user_names._local_store.pop(accepted, None)
    bot_app.user_states.pop(blocked, None)


def test_existing_slot_holder_can_register_again_after_capacity_is_full(monkeypatch):
    for number in range(30):
        assert database.claim_free_monitor_slot(f"holder-{number}") is not None
    user_id = "holder-0"
    bot_app.user_states[user_id] = "waiting_name"
    homes = []
    monkeypatch.setattr(bot_app, "reply_mode_select", lambda *_args, **_kwargs: homes.append(True))
    monkeypatch.setattr(bot_app, "claim_free_monitor_slot", database.claim_free_monitor_slot)

    bot_app.handle_text_message(_event(user_id, "再登録者"))

    assert bot_app.user_names[user_id] == "再登録者"
    assert user_id not in bot_app.user_states
    assert homes == [True]
    bot_app.user_names._local_store.pop(user_id, None)


def test_public_pc_mobile_and_production_transform_show_same_monitor_terms():
    client = bot_app.app.test_client()
    pc = client.get("/site/view/pc").get_data(as_text=True)
    mobile = client.get("/site/view/mobile").get_data(as_text=True)
    for html in (pc, mobile):
        assert "無料モニター 先着30名限定" in html
        assert "正式公開前の無料モニターとして、先着30名まで月額料金なしでご利用いただけます。" in html
        assert "30名に達した時点で、新規の無料モニター受付を終了します。" in html
        assert "料金・提供条件は公開準備中" not in html

    production_pc = refresh_public_site_html(pc, mobile=False)
    production_mobile = refresh_public_site_html(mobile, mobile=True)
    for html in (production_pc, production_mobile):
        assert "無料モニター 先着30名限定" in html
        assert "検証期間中 無料公開" not in html


def test_frozen_preview_sources_are_not_modified():
    for source in (PREVIEW_PC_DIR / "index.html", PREVIEW_724_DIR / "index.html"):
        html = Path(source).read_text(encoding="utf-8")
        assert "無料モニター 先着30名限定" not in html
