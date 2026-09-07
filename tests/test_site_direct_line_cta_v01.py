from flask import Flask

from site_direct_line_cta import install_site_direct_line_cta
from site_marketing_hotfix import install_site_marketing_hotfix
from site_marketing_refresh import install_site_marketing_refresh


def _app(monkeypatch):
    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.com/line-start")
    app = Flask(__name__)
    app.add_url_rule(
        "/site/view/pc",
        "pc",
        lambda: '''<html><head></head><body>
        <article class="faq-panel marketing-faq-panel" id="faq">
          <div class="marketing-faq-list"><details><summary>old</summary><p class="faq-answer">old</p></details></div>
          <a class="marketing-contact-link" href="/site/faq">その他の質問はこちら　›</a>
        </article>
        <a class="marketing-line-button" href="https://example.com/line-start">LINEで無料ではじめる　›</a>
        <img class="marketing-line-qr" src="/site/line-qr.svg">
        </body></html>''',
    )
    app.add_url_rule(
        "/site/view/mobile",
        "mobile",
        lambda: '''<html><head></head><body>
        <a class="marketing-line-button" href="https://example.com/line-start">LINEで無料ではじめる　›</a>
        <img class="marketing-line-qr" src="/site/line-qr.svg">
        </body></html>''',
    )
    # Flask after_request handlers run in reverse registration order.
    # Match Production: direct pass runs after hotfix and refresh.
    install_site_direct_line_cta(app)
    install_site_marketing_hotfix(app)
    install_site_marketing_refresh(app)
    return app


def test_final_cta_goes_straight_to_verified_line_url(monkeypatch):
    html = _app(monkeypatch).test_client().get("/site/view/pc").get_data(as_text=True)
    assert 'class="marketing-line-button" href="https://example.com/line-start"' in html
    assert 'target="_blank" rel="noopener noreferrer"' in html
    assert '/site/view/pc#line-start-panel">LINEで無料ではじめる' not in html
    assert '/site/line-qr.svg' in html


def test_mobile_direct_button_is_primary_and_qr_remains_secondary(monkeypatch):
    html = _app(monkeypatch).test_client().get("/site/view/mobile").get_data(as_text=True)
    assert 'class="marketing-line-button" href="https://example.com/line-start"' in html
    assert 'site-direct-line-cta-v01' in html
    assert '.marketing-mobile-free .marketing-line-start>div{order:1!important' in html
    assert '.marketing-mobile-free .marketing-line-qr{order:2!important' in html
    assert 'スマホで見ている方は、上のボタンからそのままLINEを開けます。' in html
    assert '/site/line-qr.svg' in html
