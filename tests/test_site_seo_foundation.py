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
        return (
            "<!doctype html><html lang=\"ja\"><head>"
            "<title>よくある質問 | LicenseTown</title></head>"
            "<body><h1>よくある質問</h1></body></html>"
        )

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


def test_robots_points_to_sitemap_and_blocks_only_non_public_preview_boundaries():
    client = _app().test_client()
    response = client.get("/robots.txt", base_url="https://example.test")
    text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert "Allow: /site" in text
    assert "Disallow: /site/view/" not in text
    assert "Disallow: /site/source/" in text
    assert "Disallow: /site/preview-pc/" in text
    assert "Sitemap: https://example.test/sitemap.xml" in text


def test_trailing_slash_redirects_to_canonical_site_url():
    client = _app().test_client()
    response = client.get("/site/", base_url="https://example.test")

    assert response.status_code == 301
    assert response.headers["Location"] == "/site"


def test_sitemap_contains_only_public_search_pages():
    client = _app().test_client()
    response = client.get("/sitemap.xml", base_url="https://example.test")
    text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.mimetype == "application/xml"
    assert "<loc>https://example.test/site</loc>" in text
    assert "<loc>https://example.test/site/</loc>" not in text
    assert "<loc>https://example.test/site/faq</loc>" in text
    assert "/site/view/pc" not in text
    assert "/site/source/" not in text


def test_rendered_site_view_is_crawlable_but_canonicalized_to_public_site():
    client = _app().test_client()
    response = client.get("/site/view/pc", base_url="https://example.test")

    assert response.status_code == 200
    assert "X-Robots-Tag" not in response.headers
    assert response.headers["Link"] == '<https://example.test/site>; rel="canonical"'


def test_source_and_preview_asset_responses_remain_noindex():
    client = _app().test_client()

    for path in (
        "/site/source/mobile",
        "/site/preview-pc/index.html",
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["X-Robots-Tag"] == "noindex, nofollow, noarchive"
        assert "Link" not in response.headers


def test_public_site_is_not_forced_noindex():
    client = _app().test_client()
    response = client.get("/site")

    assert response.status_code == 200
    assert "X-Robots-Tag" not in response.headers


def test_public_faq_gets_canonical_meta_and_bilingual_brand_name():
    client = _app().test_client()
    response = client.get("/site/faq", base_url="https://example.test")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert '<link rel="canonical" href="https://example.test/site/faq">' in html
    assert '<meta name="description" content="ライセンスタウン（LicenseTown）のよくある質問。' in html
    assert "<title>よくある質問｜ライセンスタウン（LicenseTown）</title>" in html
    assert "<h1>ライセンスタウン（LicenseTown）のよくある質問</h1>" in html
    assert html.count('rel="canonical"') == 1


def test_home_template_targets_pt_exam_search_intent():
    html = (ROOT / "templates" / "site" / "home.html").read_text(encoding="utf-8")

    assert "<title>ライセンスタウン（LicenseTown）｜理学療法士国家試験" in html
    assert 'name="application-name" content="ライセンスタウン"' in html
    assert "理学療法士国家試験の勉強・問題演習ならライセンスタウン" in html
    assert "PT国試" in html
    assert 'rel="canonical"' in html
    assert 'property="og:url"' in html
    assert 'property="og:site_name" content="ライセンスタウン"' in html
    assert 'application/ld+json' in html
    assert '"name":"ライセンスタウン"' in html
    assert '"alternateName":["LicenseTown","LicenseTown（ライセンスタウン）"' in html
    assert '"EducationalApplication"' in html
    assert 'name="robots" content="index,follow' in html
