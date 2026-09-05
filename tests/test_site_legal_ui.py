from flask import Flask

import site_legal_ui
from site_ui import _sale_safe_html


def test_sale_legal_ready_requires_all_operator_fields(monkeypatch):
    for env_name in site_legal_ui._REQUIRED_OPERATOR_ENV.values():
        monkeypatch.delenv(env_name, raising=False)
    monkeypatch.delenv(site_legal_ui._OPERATOR_BRAND_ENV, raising=False)
    assert site_legal_ui.sale_legal_ready() is False

    monkeypatch.setenv("SITE_SELLER_NAME", "LicenseTown operator")
    monkeypatch.setenv("SITE_SELLER_ADDRESS", "Tokyo")
    monkeypatch.setenv("SITE_SELLER_PHONE", "000-0000-0000")
    monkeypatch.setenv("SITE_SUPPORT_EMAIL", "support@example.test")
    assert site_legal_ui.sale_legal_ready() is True


def test_operator_brand_is_optional_and_rendered_when_configured(monkeypatch):
    monkeypatch.delenv(site_legal_ui._OPERATOR_BRAND_ENV, raising=False)
    assert site_legal_ui.operator_brand() == ""
    assert "運営ブランド" not in site_legal_ui._operator_rows()

    monkeypatch.setenv(site_legal_ui._OPERATOR_BRAND_ENV, "myforest")
    rows = site_legal_ui._operator_rows()
    assert "運営ブランド" in rows
    assert "myforest" in rows


def test_support_page_is_optional_and_sale_safe():
    app = Flask(__name__)
    app.register_blueprint(site_legal_ui.site_legal_ui)
    response = app.test_client().get("/site/support")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "LicenseTownを応援する" in html
    assert "支援する・しないは完全に任意" in html
    assert "現在提供している学習機能に差はつけません" in html
    assert "100円・300円・500円・1,000円" in html
    assert "1回あたり1,000円を上限" in html
    assert "それ以上の金額は受け付けません" in html
    assert "これからも「誠実」であることを大切にします" in html
    assert "現在は支援受付の準備中" in html
    assert "決済機能はまだ公開していません" in html


def test_all_public_info_pages_open_from_top_and_use_normal_page_scroll():
    app = Flask(__name__)
    app.register_blueprint(site_legal_ui.site_legal_ui)
    client = app.test_client()
    paths = (
        "/site/legal/commercial-transactions",
        "/site/legal/privacy",
        "/site/legal/terms",
        "/site/legal/operator",
        "/site/legal/contact",
        "/site/support",
    )
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200, path
        html = response.get_data(as_text=True)
        assert "body{font-family" in html
        assert "overflow-y:auto" in html
        assert "max-height:calc(100dvh" not in html
        assert "history.scrollRestoration='manual'" in html
        assert "window.scrollTo(0,0)" in html
        assert "window.addEventListener('pageshow',showFromTop)" in html
        assert "LicenseTown公式サイトへ戻る" in html


def test_public_footer_links_are_wired():
    html = "<a>特定商取引法に基づく表記</a><a>プライバシーポリシー</a><a>利用規約</a><a>運営会社</a><a>お問い合わせ</a>"
    safe = _sale_safe_html(html)
    assert '/site/legal/commercial-transactions' in safe
    assert '/site/legal/privacy' in safe
    assert '/site/legal/terms' in safe
    assert '/site/legal/operator' in safe
    assert '/site/legal/contact' in safe
    assert '/site/support' in safe
    assert 'LicenseTownを応援する' in safe
