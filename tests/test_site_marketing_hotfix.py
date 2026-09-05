from flask import Flask

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
          <h2>よくある質問</h2>
          <div class="marketing-faq-list"><details><summary>old</summary><p class="faq-answer">old</p></details></div>
          <a class="marketing-contact-link" href="/site/faq">その他の質問はこちら　›</a>
        </article>
        <a class="marketing-line-button" href="https://example.com/line-start">LINEで無料ではじめる　›</a>
        </body></html>''',
    )
    install_site_marketing_refresh(app)
    install_site_marketing_hotfix(app)
    return app


def test_hp_preview_shows_three_visible_answers_and_safe_internal_links(monkeypatch):
    app = _app(monkeypatch)
    response = app.test_client().get("/site/view/pc")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert html.count('class="marketing-faq-preview-item"') == 3
    assert "理学療法士国家試験に向けて" in html
    assert "現在は検証期間中のため" in html
    assert "ありません。将来、有料化する場合" in html
    assert 'href="/site/faq-all">その他の質問はこちら' in html
    assert 'href="/site/line-start">LINEで無料ではじめる' in html
    assert "marketing-hotfix-v03" in html


def test_full_faq_page_shows_all_ten_answers_without_accordion(monkeypatch):
    app = _app(monkeypatch)
    response = app.test_client().get("/site/faq-all")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert html.count('class="faq-item"') == 10
    assert "会員登録やパスワードは必要ですか？" in html
    assert "「教えて源さん」では何ができますか？" in html
    assert "<details" not in html


def test_line_start_page_is_never_blank_and_exposes_qr_and_explicit_action(monkeypatch):
    app = _app(monkeypatch)
    response = app.test_client().get("/site/line-start")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "LINEで無料ではじめる" in html
    assert '/site/line-qr.svg' in html
    assert 'href="https://example.com/line-start"' in html
    assert 'target="_blank"' in html
