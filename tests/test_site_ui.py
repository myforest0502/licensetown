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
    assert 'class="section-number"' in html
    assert "01" in html and "08" in html
    assert 'class="phone"' in html
    assert "30秒でわかる" in html
    assert 'class="dashboard-preview"' in html
    assert 'class="steps"' in html
    assert "寺子屋のような場所へ" in html
    assert "AIが毎回問題を作っているのですか？" in html
    assert "20260821-hero2" in html
    assert "/static/site/illustrations.svg" in html
    assert "/static/site/terakoya.svg" in html
    assert "/static/site/founding.svg" in html
    assert "/static/site/cta-phone.svg" in html
    assert "源さんから一言" in html


def test_site_static_assets_are_served():
    client = app.test_client()

    assert client.get("/static/site/site.css").status_code == 200
    assert client.get("/static/site/site.js").status_code == 200
    assert client.get("/static/images/characters/gensan_main.png").status_code == 200
    assert client.get("/static/site/illustrations.svg").status_code == 200
    assert client.get("/static/site/hero-room.svg").status_code == 200
    assert client.get("/static/site/hero-video-landscape.svg").status_code == 200
    assert client.get("/static/site/terakoya.svg").status_code == 200
    assert client.get("/static/site/founding.svg").status_code == 200
    assert client.get("/static/site/cta-phone.svg").status_code == 200


def test_site_hero_uses_reference_visual_contract():
    client = app.test_client()
    html = client.get("/site").get_data(as_text=True)
    css = client.get("/static/site/site.css").get_data(as_text=True)

    assert 'class="hero numbered-section"' in html
    assert 'class="hero-line"' in html
    assert "やったから<em>出来た子</em>へ。" in html
    assert 'class="phone"' in html
    assert 'class="video-card"' in html
    assert 'href="#try"' in html
    assert 'href="#road"' in html
    assert 'url("hero-room.svg")' in css
    assert 'url("hero-video-landscape.svg")' in css
    assert "grid-template-columns:55fr 45fr" in css
    assert "@media(max-width:390px)" in css
