import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app
from site_ui import PREVIEW_724_DIR, PREVIEW_PC_DIR


def test_site_route_renders_without_changing_existing_root():
    client = app.test_client()

    response = client.get("/site")
    root_response = client.get("/")

    assert response.status_code == 200
    assert root_response.status_code == 200
    assert root_response.get_data(as_text=True) == "License Town LINE Bot is running!"


def test_site_wrapper_uses_completed_responsive_contract():
    html = app.test_client().get("/site").get_data(as_text=True)

    assert '<meta name="viewport" content="width=device-width, initial-scale=1.0">' in html
    assert "/static/site/site.css" in html
    assert "/static/site/site.js" in html
    assert "20260824-source1" in html
    assert 'id="pc-view"' in html
    assert 'id="mobile-view"' in html
    assert 'src="/site/view/pc"' in html
    assert 'src="/site/view/mobile"' in html
    assert "data-source=" not in html


def test_site_preview_sources_and_assets_are_served():
    client = app.test_client()

    paths = (
        "/static/site/site.css",
        "/static/site/site.js",
        "/site/source/pc",
        "/site/source/mobile",
        "/site/view/pc",
        "/site/view/mobile",
        "/site/preview-pc/styles.css",
        "/site/preview-724/styles.css",
        "/site/preview-724/assets/hero-phone.png",
        "/site/preview-responsive/middle.css",
        "/site/preview-responsive/mobile.css",
    )

    for path in paths:
        assert client.get(path).status_code == 200, path


def test_site_view_routes_return_complete_same_origin_documents():
    client = app.test_client()
    pc_html = client.get("/site/view/pc").get_data(as_text=True)
    mobile_html = client.get("/site/view/mobile").get_data(as_text=True)

    assert "やれば出来る子を" in pc_html
    assert '<base href="/site/preview-pc/">' in pc_html
    assert 'href="/site/preview-responsive/middle.css"' in pc_html
    assert "LicenseTownでできること" in mobile_html
    assert '<base href="/site/preview-724/">' in mobile_html
    assert 'href="/site/preview-responsive/mobile.css"' in mobile_html


def test_site_sources_match_completed_pc_and_mobile_pages():
    client = app.test_client()
    pc_html = client.get("/site/source/pc").get_data(as_text=True)
    mobile_html = client.get("/site/source/mobile").get_data(as_text=True)

    assert "やれば出来る子を" in pc_html
    assert "three-grid" in pc_html
    assert 'class="road-card"' in pc_html
    assert "LicenseTownでできること" in mobile_html
    assert 'class="dashboard dashboard-main"' in mobile_html
    assert 'class="steps"' in mobile_html
    assert "寺子屋のような場所へ。" in mobile_html
    assert 'class="final-cta"' in mobile_html


def test_pc_lower_cards_keep_heading_on_one_line_and_faq_link_visible():
    html = (PREVIEW_PC_DIR / "index.html").read_text(encoding="utf-8")
    css = (PREVIEW_PC_DIR / "trust-support.css").read_text(encoding="utf-8")

    assert "ライセンスタウンは、あなたの「合格したい」を応援します。" in html
    assert "「合格したい」を全力で応援します。" not in html
    assert "その他の質問はこちら" in html
    assert ".brand-panel h2{" in css
    assert "white-space:nowrap" in css
    assert ".faq-panel{overflow:visible!important;padding-bottom:16px!important}" in css
    assert ".faq-panel>a{margin-top:6px!important;padding-bottom:2px}" in css


def test_pc_trust_support_copy_states_current_free_and_optional_support_policy():
    html = (PREVIEW_PC_DIR / "index.html").read_text(encoding="utf-8")

    assert "まだ完成したサービスだとは考えていません" in html
    assert "月額料金をお願いしません" in html
    assert "もっとレスポンスを速くしたい" in html
    assert "100円からの開発支援" in html
    assert "1回あたり1,000円まで" in html
    assert "支援は完全に任意です" in html
    assert "支援の有無で、現在の学習機能に差はありません" in html
    assert "LicenseTownの改善・運営・開発のために使います" in html


def test_mobile_public_view_gets_trust_support_copy_without_mutating_frozen_724_source():
    client = app.test_client()
    mobile_html = client.get("/site/view/mobile").get_data(as_text=True)
    raw_724_html = (PREVIEW_724_DIR / "index.html").read_text(encoding="utf-8")

    assert 'class="mobile-trust-support"' in mobile_html
    assert "迷ったときは、「それは誠実か？」で考える。" in mobile_html
    assert "まだ完成したサービスだとは考えていません" in mobile_html
    assert "月額料金をお願いしません" in mobile_html
    assert "100円からの開発支援" in mobile_html
    assert "1回あたり1,000円まで" in mobile_html
    assert "支援は完全に任意" in mobile_html
    assert "支援の有無で現在の学習機能に差はありません" in mobile_html
    assert "LicenseTownの改善・運営・開発のために使います" in mobile_html
    assert 'class="mobile-trust-support"' not in raw_724_html


def test_mobile_public_trust_support_is_stacked_before_final_cta_and_has_canvas_room():
    client = app.test_client()
    mobile_html = client.get("/site/view/mobile").get_data(as_text=True)
    mobile_css = client.get("/site/preview-responsive/mobile.css").get_data(as_text=True)

    assert mobile_html.index('class="mobile-trust-support"') < mobile_html.index('class="final-cta"')
    assert ".page{height:2624px!important}" in mobile_css
    assert ".mobile-trust-support{position:relative;width:724px;height:452px" in mobile_css
    assert ".mobile-principles-card{top:12px;height:166px" in mobile_css
    assert ".mobile-support-card{top:188px;height:250px}" in mobile_css
    assert ".mobile-support-amounts{position:static" in mobile_css
    assert ".mobile-support-cap{position:static" in mobile_css
    assert ".mobile-support-card>a{position:static" in mobile_css
    assert ".mobile-support-card>small{position:static" in mobile_css


def test_site_keeps_724_canvas_scaling_and_pc_mobile_switch():
    client = app.test_client()
    css = client.get("/static/site/site.css").get_data(as_text=True)
    js = client.get("/static/site/site.js").get_data(as_text=True)
    middle_css = client.get("/site/preview-responsive/middle.css").get_data(as_text=True)

    assert "@media(max-width:767px)" in css
    assert ".pc-view{display:none}" in css
    assert "document.documentElement.clientWidth/724" in js
    assert "scale(${scale})" in js
    assert "frame.addEventListener('load',syncFrame)" in js
    assert "frame.srcdoc" not in js
    assert "fetch(" not in js
    assert "(min-width:724px) and (max-width:1179px)" in middle_css
    assert ".brand-panel,.faq-panel,.try-panel{height:190px!important;min-height:190px!important}" in middle_css
    assert ".faq-panel{padding:10px 14px 15px!important;overflow:visible!important}" in middle_css
    assert ".faq-panel h2{font-size:18px!important" in middle_css
    assert ".faq-panel p{min-height:24px!important;padding:4px!important;font-size:11px!important" in middle_css
    assert ".faq-panel>a{display:block;margin-top:3px!important;padding-bottom:3px!important;font-size:11px!important" in middle_css
