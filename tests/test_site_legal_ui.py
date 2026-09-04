import site_legal_ui
from site_ui import _sale_safe_html


def test_sale_legal_ready_requires_all_operator_fields(monkeypatch):
    for env_name in site_legal_ui._REQUIRED_OPERATOR_ENV.values():
        monkeypatch.delenv(env_name, raising=False)
    assert site_legal_ui.sale_legal_ready() is False

    monkeypatch.setenv("SITE_SELLER_NAME", "LicenseTown operator")
    monkeypatch.setenv("SITE_SELLER_ADDRESS", "Tokyo")
    monkeypatch.setenv("SITE_SELLER_PHONE", "000-0000-0000")
    monkeypatch.setenv("SITE_SUPPORT_EMAIL", "support@example.test")
    assert site_legal_ui.sale_legal_ready() is True


def test_public_footer_links_are_wired():
    html = "<a>特定商取引法に基づく表記</a><a>プライバシーポリシー</a><a>利用規約</a><a>運営会社</a><a>お問い合わせ</a>"
    safe = _sale_safe_html(html)
    assert '/site/legal/commercial-transactions' in safe
    assert '/site/legal/privacy' in safe
    assert '/site/legal/terms' in safe
    assert '/site/legal/operator' in safe
    assert '/site/legal/contact' in safe
