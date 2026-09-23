import os
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from wsgi import app


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_public_views_present_free_beta_conversion_without_touching_frozen_sources(monkeypatch):
    target = "https://example.com/licensetown-line"
    monkeypatch.setenv("SITE_ONBOARDING_URL", target)
    client = app.test_client()

    for path in ("/site/view/pc", "/site/view/mobile"):
        html = client.get(path).get_data(as_text=True)
        assert "第62回 理学療法士国家試験を受験する方へ" in html
        assert "無料βモニター 先着30名募集中" in html
        assert "LINEで無料βを始める" in html
        assert f'href="{target}"' in html
        assert "やれば出来る子を、" in html
        assert "やったから" in html
        assert "教えて源さん" in html

    mobile_html = client.get("/site/view/mobile").get_data(as_text=True)
    assert "寺子屋のような場所" in mobile_html
    assert "はじまりは、息子一人のためでした。" in mobile_html

    assert "無料βモニター 先着30名募集中" not in (
        REPO_ROOT / "preview-pc" / "index.html"
    ).read_text(encoding="utf-8")
    assert "無料βモニター 先着30名募集中" not in (
        REPO_ROOT / "preview-724" / "index.html"
    ).read_text(encoding="utf-8")


def test_pc_keeps_qr_and_places_support_after_free_beta_cta(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/pc").get_data(as_text=True)

    assert 'class="marketing-line-qr"' in html
    assert html.index('class="bottom"') < html.index('class="trust-support"')
    assert "100円からの開発支援" in html


def test_mobile_prioritizes_button_and_hides_qr_with_dedicated_css(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/mobile").get_data(as_text=True)

    assert 'class="marketing-line-button"' in html
    assert ".marketing-mobile-free .marketing-line-qr{display:none!important}" in html
    assert html.index('class="final-cta"') < html.index('class="mobile-trust-support"')


def test_public_question_counts_remain_formal_bank_values(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/pc").get_data(as_text=True)

    assert "1643" in html
    assert "1100" in html
    assert "2743" in html



def test_pc_hero_separates_audience_action_and_question_volume(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/pc").get_data(as_text=True)

    assert "@media(min-width:761px)" in html
    assert ".hero{height:370px!important}" in html
    assert ".hero .free-beta-hero-notice{margin:20px 0 0!important}" in html
    assert ".hero .hero-actions{margin-top:22px!important}" in html
    assert ".hero .hero-actions .secondary" in html
    assert "LINEで無料βを始める" in html
    assert "合格への道を見る" in html
    notice_pos = html.index('<div class="free-beta-hero-notice"')
    primary_pos = html.index('<a class="btn primary"', notice_pos)
    stats_pos = html.index('<section class="stats"', primary_pos)
    assert notice_pos < primary_pos < stats_pos




def test_pc_hero_tags_are_readable_but_remain_below_primary_cta(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/pc").get_data(as_text=True)

    assert ".hero .free-beta-hero-notice strong,.hero .free-beta-hero-notice span{min-height:32px!important;padding:7px 13px!important;font-size:14px!important}" in html
    assert ".hero .free-beta-hero-notice span{font-size:15px!important;font-weight:800!important" in html
    assert ".marketing-line-button{display:inline-block!important" in html
    assert "font-weight:700!important" in html

def test_public_home_has_no_stale_2000_question_copy():
    html = app.test_client().get("/site").get_data(as_text=True)

    assert "2000問" not in html
    assert "2743問の問題演習" in html
