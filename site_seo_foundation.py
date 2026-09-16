from __future__ import annotations

from html import escape

from flask import Response, redirect, request


NOINDEX_PREFIXES = (
    "/site/source/",
    "/site/preview-pc/",
    "/site/preview-724/",
    "/site/preview-responsive/",
)

GSC_VERIFICATION_FILES = (
    "googlef6f9c91620140fb4.html",
)


def _origin() -> str:
    return request.url_root.rstrip("/")


def _enhance_public_faq_html(response):
    """Add stable SEO signals to the existing public FAQ without owning its UI."""
    if request.path != "/site/faq" or response.status_code != 200:
        return response
    if not response.mimetype or "html" not in response.mimetype:
        return response

    html = response.get_data(as_text=True)
    canonical = f"{_origin()}/site/faq"
    description = (
        "ライセンスタウン（LicenseTown）のよくある質問。理学療法士国家試験の学習、"
        "LINEでの利用、無料モニター、見守り機能などについて案内します。"
    )

    html = html.replace(
        "<title>よくある質問 | LicenseTown</title>",
        "<title>よくある質問｜ライセンスタウン（LicenseTown）</title>",
        1,
    )
    if 'rel="canonical"' not in html:
        html = html.replace(
            "</head>",
            f'<link rel="canonical" href="{escape(canonical, quote=True)}">'
            f'<meta name="description" content="{escape(description, quote=True)}">'
            '<meta name="application-name" content="ライセンスタウン">'
            '<meta property="og:site_name" content="ライセンスタウン">'
            "</head>",
            1,
        )
    if "<h1>ライセンスタウン（LicenseTown）のよくある質問</h1>" not in html:
        html = html.replace(
            "<h1>よくある質問</h1>",
            "<h1>ライセンスタウン（LicenseTown）のよくある質問</h1>",
            1,
        )

    response.set_data(html)
    return response


def install_site_seo_foundation(app) -> None:
    """Install public SEO discovery routes without changing the frozen site UI."""

    def licensetown_gsc_verification(filename: str):
        return Response(
            f"google-site-verification: {filename}\n",
            mimetype="text/plain",
        )

    for filename in GSC_VERIFICATION_FILES:
        app.add_url_rule(
            f"/{filename}",
            endpoint=f"licensetown_gsc_verification_{filename}",
            view_func=lambda filename=filename: licensetown_gsc_verification(filename),
            methods=["GET"],
        )

    @app.get("/site/")
    def licensetown_site_trailing_slash_redirect():
        return redirect("/site", code=301)

    @app.get("/robots.txt")
    def licensetown_robots():
        origin = _origin()
        body = "\n".join(
            (
                "User-agent: *",
                "Allow: /site",
                "Disallow: /site/source/",
                "Disallow: /site/preview-pc/",
                "Disallow: /site/preview-724/",
                "Disallow: /site/preview-responsive/",
                f"Sitemap: {origin}/sitemap.xml",
                "",
            )
        )
        return Response(body, mimetype="text/plain")

    @app.get("/sitemap.xml")
    def licensetown_sitemap():
        origin = escape(_origin(), quote=True)
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f'<url><loc>{origin}/site</loc></url>'
            f'<url><loc>{origin}/site/faq</loc></url>'
            '</urlset>'
        )
        return Response(body, mimetype="application/xml")

    @app.after_request
    def apply_site_seo_headers(response):
        response = _enhance_public_faq_html(response)
        path = request.path
        if path.startswith("/site/view/"):
            response.headers["Link"] = f'<{_origin()}/site>; rel="canonical"'
        elif any(path.startswith(prefix) for prefix in NOINDEX_PREFIXES):
            response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response
