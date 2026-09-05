from flask import Flask

from site_marketing_viewport_fix import install_site_marketing_viewport_fix


def _app():
    app = Flask(__name__)
    app.add_url_rule(
        "/site/view/pc",
        "pc",
        lambda: '''<html><head></head><body>
        <a class="marketing-contact-link" href="/site/view/pc#faq-all-panel">その他の質問はこちら</a>
        <a class="marketing-line-button" href="/site/view/pc#line-start-panel">LINEで無料ではじめる</a>
        <section id="faq-all-panel" class="marketing-modal-overlay"><div class="marketing-modal-card"><a class="marketing-modal-close" href="/site/view/pc#faq">×</a>FAQ</div></section>
        <section id="line-start-panel" class="marketing-modal-overlay"><div class="marketing-modal-card"><a class="marketing-modal-close" href="/site/view/pc#try">×</a>LINE</div></section>
        <section class="brand-panel"><h2>ライセンスタウンは、あなたの「合格したい」を応援します。</h2></section>
        </body></html>''',
    )
    install_site_marketing_viewport_fix(app)
    return app


def test_overlay_clicks_are_intercepted_without_hash_navigation():
    html = _app().test_client().get("/site/view/pc").get_data(as_text=True)
    assert '.marketing-modal-overlay.is-open{display:flex!important' in html
    assert "faqLink.addEventListener('click'" in html
    assert "lineLink.addEventListener('click'" in html
    assert "event.preventDefault();" in html
    assert "panel.classList.add('is-open')" in html
    assert "panel.scrollTop=0" in html
    assert "card.scrollTop=0" in html
    assert "panel.showModal()" in html
    assert "panel.close()" in html
    assert "window.scrollTo(savedScrollX,savedScrollY)" in html
    assert "dialog.marketing-modal-overlay{width:100vw!important;height:100dvh!important" in html


def test_overlays_are_anchored_to_viewport_bottom():
    html = _app().test_client().get("/site/view/pc").get_data(as_text=True)
    assert '.marketing-modal-overlay.is-open{display:flex!important;align-items:flex-end!important' in html
    assert '.marketing-modal-overlay:target{align-items:flex-end!important' in html
    assert 'margin:0 auto 16px!important' in html
    assert 'scroll-margin-bottom:0!important' in html


def test_brand_headline_is_shrunk_without_truncating_text():
    html = _app().test_client().get("/site/view/pc").get_data(as_text=True)
    assert 'ライセンスタウンは、あなたの「合格したい」を応援します。' in html
    assert '.brand-panel h2{font-size:15px!important' in html
    assert 'white-space:nowrap!important' in html
