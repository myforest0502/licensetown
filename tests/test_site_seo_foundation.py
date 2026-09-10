from pathlib import Path

from flask import Flask

from site_seo_foundation import install_site_seo_foundation


ROOT = Path(__file__).resolve().parents[1]


def _app():
    app = Flask(__name__)

    @app.get("/site")
    def site_home():
        return "site"

    @app.get("/site/faq")
    def site_faq():
        return "faq"

    @app.get("/site/view/pc")
    def preview_pc():
        return "preview"

    @app.get("/site/source/mobile")
    def source_mobile():
        return "source"

    @app.get("/site/preview-pc/index.html")
    def preview_asset_html():
        return "asset"

    install_site_seo_foundation(app)
    return app


def test_robots_points_to_sitemap_and_blocks_preview_boundaries():
    client = _app().test_client()
    response = client.get("/robots.txt", base_url="https://example.test")
    text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert "Allow: /site" in text
    assert "Disallow: /site/view/" in text
    assert "Disallow: /site/source/" in text
    assert "Disallow: /site/preview-pc/" in text
    assert "Sitemap: https://example.test/sitemap.xml" in text


def test_sitemap_contains_only_public_search_pages():
    client = _app().test_client()
    response = client.get("/sitemap.xml", base_url="https://example.test")
    text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.mimetype == "application/xml"
    assert "https://example.test/site" in text
    assert "https://example.test/site/faq" in text
    assert "/site/view/pc" not in text
    assert "/site/source/" not in text


def test_preview_and_source_responses_are_noindex():
    client = _app().test_client()

    for path in (
        "/site/view/pc",
        "/site/source/mobile",
        "/site/preview-pc/index.html",
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["X-Robots-Tag"] == "noindex, nofollow, noarchive"


def test_public_site_is_not_forced_noindex():
    client = _app().test_client()
    response = client.get("/site")

    assert response.status_code == 200
    assert "X-Robots-Tag" not in response.headers


def test_home_template_targets_pt_exam_search_intent():
    html = (ROOT / "templates" / "site" / "home.html").read_text(encoding="utf-8")

    assert "理学療法士国家試験の勉強・問題演習ならLicenseTown" in html
    assert "PT国試" in html
    assert 'rel="canonical"' in html
    assert 'property="og:url"' in html
    assert 'application/ld+json' in html
    assert '"EducationalApplication"' in html
    assert 'name="robots" content="index,follow' in html
