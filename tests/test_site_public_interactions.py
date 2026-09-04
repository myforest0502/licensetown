import os

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


def test_mobile_faq_has_answers_and_single_open_accordion_behavior():
    client = app.test_client()
    html = client.get("/site/view/mobile").get_data(as_text=True)
    css = client.get("/site/preview-responsive/mobile.css").get_data(as_text=True)

    assert html.count('class="faq-answer"') == 4
    assert "月額料金はお願いしていません" in html
    assert "一部の画面はブラウザで開いて確認します" in html
    assert "個別の相談内容は共有されません" in html
    assert "理学療法士国家試験に向けて" in html
    assert "if (other !== item) other.open = false" in html
    assert '.faq-list details[open] summary:after{content:"−"}' in css
    assert ".faq-answer{" in css
    assert ".story-faq{height:286px!important" in css
