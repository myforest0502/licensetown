from flask import Flask

from site_marketing_refresh import FAQ_ITEMS, install_site_marketing_refresh, refresh_public_site_html


def test_pc_refresh_removes_login_and_expands_faq_and_free_cta(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/line-start")
    source = '''
    <html><head></head><body>
      <div class="header-actions"><span class="btn login public-static-control" aria-disabled="true">ログイン（準備中）</span></div>
      <article class="faq-panel" id="faq"><h2>よくある質問</h2><p>古い質問</p><a>その他の質問はこちら　›</a></article>
      <article class="try-panel" id="try"><h2>サービス提供準備中</h2><p>正式な料金・提供条件は、公開前にこのページでご案内します。</p><a>まずは使ってみる　›</a></article>
    </body></html>
    '''
    html = refresh_public_site_html(source, mobile=False)
    assert "ログイン" not in html
    assert "サービス提供準備中" not in html
    assert "検証期間中 無料公開" in html
    assert "LINEで無料ではじめる" in html
    assert "/site/line-qr.svg" in html
    assert "解決しない場合はお問い合わせください" in html
    assert html.count("<details>") == len(FAQ_ITEMS) == 12
    for question, _answer in FAQ_ITEMS:
        assert question in html


def test_mobile_refresh_replaces_existing_four_item_faq(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/line-start")
    source = '''
    <html><head></head><body>
      <article class="faq-card"><h2>よくあるご質問</h2><div class="faq-list"><details><summary>料金はかかりますか？</summary><p class="faq-answer">old</p></details></div></article>
      <section class="final-cta" id="try"><div class="cta-banner"><h2>まずは使ってみる</h2></div></section>
    </body></html>
    '''
    html = refresh_public_site_html(source, mobile=True)
    assert html.count("<details>") == 12
    assert "検証期間中 無料公開" in html
    assert "marketing-mobile-free" in html
    assert "あとから勝手に料金が発生することはありますか？" in html


def test_missing_onboarding_url_fails_closed_without_broken_qr(monkeypatch):
    monkeypatch.delenv("SITE_ONBOARDING_URL", raising=False)
    source = '<html><head></head><body><article class="try-panel" id="try"><h2>サービス提供準備中</h2></article></body></html>'
    html = refresh_public_site_html(source, mobile=False)
    assert "/site/line-qr.svg" not in html
    assert "利用開始について問い合わせる" in html
    assert "LINEの利用開始リンクを準備中" in html


def test_qr_route_returns_svg_for_verified_https_target(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/line-start")
    app = Flask(__name__)
    install_site_marketing_refresh(app)
    response = app.test_client().get("/site/line-qr.svg")
    assert response.status_code == 200
    assert response.mimetype == "image/svg+xml"
    assert b"<svg" in response.data


def test_qr_route_is_404_without_verified_target(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "javascript:alert(1)")
    app = Flask(__name__)
    install_site_marketing_refresh(app)
    response = app.test_client().get("/site/line-qr.svg")
    assert response.status_code == 404
