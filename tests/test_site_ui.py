import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app


def test_site_route_renders_without_changing_existing_root():
    client = app.test_client()

    response = client.get("/site")
    root_response = client.get("/")

    assert response.status_code == 200
    assert root_response.status_code == 200
    assert root_response.get_data(as_text=True) == "License Town LINE Bot is running!"


def test_site_wrapper_uses_completed_responsive_contract():
    html = app.test_client().get("/site").get_data(as_text=True)

    assert '<meta name="viewport" content="width=device-width, initial-scale=1.0">' in html
    assert "/static/site/site.css" in html
    assert "/static/site/site.js" in html
    assert "20260824-source1" in html
    assert 'id="pc-view"' in html
    assert 'id="mobile-view"' in html
    assert 'src="/site/view/pc"' in html
    assert 'src="/site/view/mobile"' in html
    assert "data-source=" not in html


def test_site_preview_sources_and_assets_are_served():
    client = app.test_client()

    paths = (
        "/static/site/site.css",
        "/static/site/site.js",
        "/site/source/pc",
        "/site/source/mobile",
        "/site/view/pc",
        "/site/view/mobile",
        "/site/preview-pc/styles.css",
        "/site/preview-724/styles.css",
        "/site/preview-724/assets/hero-phone.png",
        "/site/preview-responsive/middle.css",
        "/site/preview-responsive/mobile.css",
    )

    for path in paths:
        assert client.get(path).status_code == 200, path


def test_site_view_routes_return_complete_same_origin_documents():
    client = app.test_client()
    pc_html = client.get("/site/view/pc").get_data(as_text=True)
    mobile_html = client.get("/site/view/mobile").get_data(as_text=True)

    assert "やれば出来る子を" in pc_html
    assert '<base href="/site/preview-pc/">' in pc_html
    assert 'href="/site/preview-responsive/middle.css"' in pc_html
    assert "LicenseTownでできること" in mobile_html
    assert '<base href="/site/preview-724/">' in mobile_html
    assert 'href="/site/preview-responsive/mobile.css"' in mobile_html


def test_site_sources_match_completed_pc_and_mobile_pages():
    client = app.test_client()
    pc_html = client.get("/site/source/pc").get_data(as_text=True)
    mobile_html = client.get("/site/source/mobile").get_data(as_text=True)

    assert "やれば出来る子を" in pc_html
    assert "three-grid" in pc_html
    assert 'class="road-card"' in pc_html
    assert "LicenseTownでできること" in mobile_html
    assert 'class="dashboard dashboard-main"' in mobile_html
    assert 'class="steps"' in mobile_html
    assert "寺子屋のような場所へ。" in mobile_html
    assert 'class="final-cta"' in mobile_html


def test_site_keeps_724_canvas_scaling_and_pc_mobile_switch():
    client = app.test_client()
    css = client.get("/static/site/site.css").get_data(as_text=True)
    js = client.get("/static/site/site.js").get_data(as_text=True)
    middle_css = client.get("/site/preview-responsive/middle.css").get_data(as_text=True)

    assert "@media(max-width:767px)" in css
    assert ".pc-view{display:none}" in css
    assert "document.documentElement.clientWidth/724" in js
    assert "scale(${scale})" in js
    assert "frame.addEventListener('load',syncFrame)" in js
    assert "frame.srcdoc" not in js
    assert "fetch(" not in js
    assert "(min-width:724px) and (max-width:1179px)" in middle_css
