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
    # Production order: after_request executes in reverse registration order,
    # so register the hotfix first and the normal refresh second.
    install_site_marketing_hotfix(app)
    install_site_marketing_refresh(app)
    return app


def test_hp_preview_shows_three_readable_answers_and_in_page_actions(monkeypatch):
    app = _app(monkeypatch)
    response = app.test_client().get("/site/view/pc")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert html.count('class="marketing-faq-preview-item"') == 3
    assert "理学療法士国家試験に向けて" in html
    assert "現在は検証期間中のため" in html
    assert "ありません。将来、有料化する場合" in html
    assert 'href="/site/view/pc#faq-all-panel">その他の質問はこちら' in html
    assert 'href="/site/view/pc#line-start-panel">LINEで無料ではじめる' in html
    assert "marketing-hotfix-v04" in html
    assert "height:auto!important" in html
    assert "white-space:normal!important" in html


def test_hp_contains_all_ten_questions_in_same_page_overlay(monkeypatch):
    app = _app(monkeypatch)
    html = app.test_client().get("/site/view/pc").get_data(as_text=True)
    assert 'id="faq-all-panel"' in html
    assert html.count('class="marketing-modal-faq-item"') == 10
    assert "会員登録やパスワードは必要ですか？" in html
    assert "「教えて源さん」では何ができますか？" in html


def test_hp_line_button_opens_nonblank_same_page_overlay(monkeypatch):
    app = _app(monkeypatch)
    html = app.test_client().get("/site/view/pc").get_data(as_text=True)
    assert 'id="line-start-panel"' in html
    assert '/site/line-qr.svg' in html
    assert 'href="https://example.com/line-start"' in html
    assert "LINEを開く" in html


def test_full_faq_page_shows_all_ten_answers_without_accordion(monkeypatch):
    app = _app(monkeypatch)
    response = app.test_client().get("/site/faq-all")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert html.count('class="faq-item"') == 10
    assert "会員登録やパスワードは必要ですか？" in html
    assert "「教えて源さん」では何ができますか？" in html
    assert "<details" not in html
    assert "window.scrollTo(0,0)" in html


def test_line_start_page_is_never_blank_and_exposes_qr_and_explicit_action(monkeypatch):
    app = _app(monkeypatch)
    response = app.test_client().get("/site/line-start")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "LINEで無料ではじめる" in html
    assert '/site/line-qr.svg' in html
    assert 'href="https://example.com/line-start"' in html
    assert 'target="_blank"' in html
    assert "window.scrollTo(0,0)" in html
