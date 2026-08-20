import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app
from site_ui import QUESTION_COUNT_LABEL


def test_site_route_renders_without_changing_existing_root():
    client = app.test_client()

    response = client.get("/site")
    root_response = client.get("/")

    assert response.status_code == 200
    assert root_response.status_code == 200
    assert root_response.get_data(as_text=True) == "License Town LINE Bot is running!"


def test_site_contains_core_copy_metadata_and_assets():
    response = app.test_client().get("/site")
    html = response.get_data(as_text=True)

    assert '<meta name="viewport"' in html
    assert "やれば出来る子を" in html
    assert "無料期間実施中！" in html
    assert "相談内容や個人的な会話" in html
    assert QUESTION_COUNT_LABEL in html
    assert "/static/site/site.css" in html
    assert "/static/site/site.js" in html
    assert "/static/images/characters/gensan_main.png" in html


def test_site_static_assets_are_served():
    client = app.test_client()

    assert client.get("/static/site/site.css").status_code == 200
    assert client.get("/static/site/site.js").status_code == 200
    assert client.get("/static/images/characters/gensan_main.png").status_code == 200
