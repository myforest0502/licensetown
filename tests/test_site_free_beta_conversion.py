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



def test_mobile_public_view_uses_real_responsive_layout(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/mobile").get_data(as_text=True)

    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in html
    assert 'id="mobile-responsive-overhaul-v01"' in html
    assert ".section-no{display:none!important}" in html
    assert ".main-nav{display:none!important}" in html
    assert ".hero-copy{position:static!important;width:100%!important;display:flex!important;flex-direction:column!important}" in html
    assert ".mobile-hero-actions{order:4!important" in html
    assert ".hero .chips{order:5!important" in html
    assert ".problem-grid,.feature-grid" in html
    assert "grid-template-columns:repeat(2,minmax(0,1fr))!important" in html
    assert ".steps{position:static!important;width:100%!important;height:auto!important;display:flex!important;flex-direction:column!important" in html
    assert ".story-faq{display:block!important}" in html
    assert ".footer nav{position:static!important;height:auto!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important" in html


def test_mobile_first_view_keeps_full_beta_copy_and_formal_counts(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/mobile").get_data(as_text=True)

    assert "第62回 理学療法士国家試験を受験する方へ" in html
    assert "無料βモニター 先着30名募集中" in html
    assert 'class="mobile-hero-primary"' in html
    assert "LINEで無料βを始める" in html
    assert 'class="mobile-hero-secondary"' in html
    assert "合格への道を見る" in html
    assert 'class="mobile-question-stats"' in html
    assert "1643" in html
    assert "1100" in html
    assert "2743" in html
    assert ".hero .free-beta-hero-notice strong,.hero .free-beta-hero-notice span" in html
    assert "white-space:normal!important;overflow:visible!important" in html


def test_mobile_conversion_stays_qr_free_and_footer_is_complete(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/mobile").get_data(as_text=True)

    assert ".marketing-mobile-free .marketing-line-qr{display:none!important}" in html
    assert ".marketing-mobile-free .marketing-qr-help{display:none!important}" in html
    assert "特定商取引法に基づく表記" in html
    assert "プライバシーポリシー" in html
    assert "利用規約" in html
    assert "運営情報" in html
    assert "お問い合わせ" in html
    assert "LicenseTownを応援する" in html


def test_pc_view_does_not_receive_mobile_overhaul(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/pc").get_data(as_text=True)

    assert 'id="mobile-responsive-overhaul-v01"' not in html
    assert 'class="mobile-question-stats"' not in html
    assert '<meta name="viewport" content="width=1499">' in html


def test_public_shell_no_longer_scales_724_mobile_canvas():
    css = (REPO_ROOT / "static" / "site" / "site.css").read_text(encoding="utf-8")
    js = (REPO_ROOT / "static" / "site" / "site.js").read_text(encoding="utf-8")

    assert ".mobile-view{width:100%;transform:none" in css
    assert "document.documentElement.clientWidth/724" not in js
    assert "frame.style.width='100%'" in js
    assert "frame.style.transform='none'" in js



def test_mobile_final_polish_removes_dashboard_gap_and_compacts_steps(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/mobile").get_data(as_text=True)

    assert ".dashboard-main .time,.dashboard-main .progress-card,.dashboard-main .mentor-card{grid-column:1/-1!important}" in html
    assert ".steps article{width:100%!important;height:auto!important;min-height:132px!important" in html
    assert ".steps img{left:52px!important;top:42px!important;width:60px!important;height:60px!important" in html


def test_mobile_beta_copy_uses_natural_japanese_wrapping(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/mobile").get_data(as_text=True)

    assert ".marketing-mobile-free .marketing-free-copy{font-size:14px!important;line-height:1.8!important;text-align:left!important;word-break:normal!important;overflow-wrap:normal!important;line-break:strict!important}" in html


def test_pc_view_has_no_mobile_final_polish_rules(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/licensetown-line")
    html = app.test_client().get("/site/view/pc").get_data(as_text=True)

    assert ".dashboard-main .time,.dashboard-main .progress-card,.dashboard-main .mentor-card{grid-column:1/-1!important}" not in html
    assert "min-height:132px!important" not in html
