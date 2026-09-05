from flask import Flask

from site_marketing_viewport_fix import install_site_marketing_viewport_fix


def _app():
    app = Flask(__name__)
    app.add_url_rule(
        "/site/view/pc",
        "pc",
        lambda: '''<html><head></head><body>
        <section id="faq-all-panel" class="marketing-modal-overlay"><div class="marketing-modal-card">FAQ</div></section>
        <section class="brand-panel"><h2>ライセンスタウンは、あなたの「合格したい」を応援します。</h2></section>
        </body></html>''',
    )
    install_site_marketing_viewport_fix(app)
    return app


def test_overlay_is_forced_to_open_from_viewport_top():
    html = _app().test_client().get("/site/view/pc").get_data(as_text=True)
    assert '.marketing-modal-overlay:target{align-items:flex-start!important' in html
    assert 'margin:0 auto!important' in html
    assert 'panel.scrollTop=0' in html
    assert 'card.scrollTop=0' in html


def test_brand_headline_is_shrunk_without_truncating_text():
    html = _app().test_client().get("/site/view/pc").get_data(as_text=True)
    assert 'ライセンスタウンは、あなたの「合格したい」を応援します。' in html
    assert '.brand-panel h2{font-size:15px!important' in html
    assert 'white-space:nowrap!important' in html
