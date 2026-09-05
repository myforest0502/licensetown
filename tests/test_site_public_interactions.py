import os
import re

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app


def test_preview_hash_links_stay_on_rendered_documents_despite_asset_base():
    client = app.test_client()
    pc_html = client.get("/site/view/pc").get_data(as_text=True)
    mobile_html = client.get("/site/view/mobile").get_data(as_text=True)

    assert 'href="/site/view/pc#features"' in pc_html
    assert 'href="/site/view/pc#faq"' in pc_html
    assert 'href="/site/view/mobile#features"' in mobile_html
    assert 'href="/site/view/mobile#howto"' in mobile_html
    assert 'href="/site/view/mobile#parents"' in mobile_html
    assert 'href="/site/view/mobile#faq"' in mobile_html
    assert 'href="/site/view/mobile#contact"' in mobile_html


def test_mobile_footer_operator_and_legal_links_are_public_routes():
    client = app.test_client()
    html = client.get("/site/view/mobile").get_data(as_text=True)

    assert '<a href="/site/legal/terms">利用規約</a>' in html
    assert '<a href="/site/legal/privacy">プライバシーポリシー</a>' in html
    assert '<a href="/site/legal/contact">お問い合わせ</a>' in html
    assert '<a href="/site/legal/operator">運営情報</a>' in html

    for path in (
        "/site/legal/terms",
        "/site/legal/privacy",
        "/site/legal/contact",
        "/site/legal/operator",
    ):
        assert client.get(path).status_code == 200, path


def test_mobile_faq_has_compact_answer_preview_and_single_open_accordion_behavior():
    client = app.test_client()
    html = client.get("/site/view/mobile").get_data(as_text=True)
    css = client.get("/site/preview-responsive/mobile.css").get_data(as_text=True)

    assert html.count('class="faq-answer"') == 3
    assert "検証期間中のため、利用料金はいただいていません" in html
    assert "理学療法士国家試験に向けて" in html
    assert (
        'href="/site/view/mobile#faq-all-panel">その他の質問はこちら' in html
        or 'href="/site/faq-all">その他の質問はこちら' in html
        or 'href="/site/faq">その他の質問はこちら' in html
    )
    assert client.get("/site/faq").status_code == 200
    assert "if (other !== item) other.open = false" in html
    assert '.faq-list details[open] summary:after{content:"−"}' in css
    assert ".faq-answer{" in css
    assert ".story-faq{height:286px!important" in css


def test_pc_public_document_has_no_href_less_anchor_affordances():
    html = app.test_client().get("/site/view/pc").get_data(as_text=True)

    assert not re.search(r"<a\b(?![^>]*\bhref=)[^>]*>", html)
    assert "ログイン（準備中）" not in html
    assert '<span class="detail public-static-control"' in html
    assert '表示イメージ</span>' in html
    assert (
        '<a class="marketing-contact-link" href="/site/view/pc#faq-all-panel">その他の質問はこちら' in html
        or '<a class="marketing-contact-link" href="/site/faq-all">その他の質問はこちら' in html
        or '<a class="marketing-contact-link" href="/site/faq">その他の質問はこちら' in html
    )


def test_mobile_public_video_is_static_and_clearly_not_ready():
    html = app.test_client().get("/site/view/mobile").get_data(as_text=True)

    assert '<button class="video-card"' not in html
    assert '<div class="video-card video-card-static"' in html
    assert '<span class="video-status">紹介動画<br>準備中</span>' in html
    assert '<span class="play">▶</span>' not in html


def test_mobile_dashboard_mock_controls_are_inert_but_keep_layout_classes():
    html = app.test_client().get("/site/view/mobile").get_data(as_text=True)

    assert '<span class="active public-static-control" aria-disabled="true">⌂ ダッシュボード</span>' in html
    assert '<span class="public-static-control" aria-disabled="true">すべて見る ›</span>' in html
    assert '<span class="public-static-control" aria-disabled="true">苦手を詳しく見る ›</span>' in html
    assert '<span class="public-static-control" aria-disabled="true">おすすめをもっと見る ›</span>' in html
    assert not re.search(r"<a\b(?![^>]*\bhref=)[^>]*>", html)


def test_frozen_mobile_source_keeps_original_design_contract():
    source = app.test_client().get("/site/preview-724/index.html").get_data(as_text=True)

    assert '<button class="video-card" type="button"' in source
    assert '<span class="play">▶</span>' in source
    assert "紹介動画<br>準備中" not in source
