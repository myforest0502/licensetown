from __future__ import annotations

from html import escape

from flask import Response, request


NOINDEX_PREFIXES = (
    "/site/view/",
    "/site/source/",
    "/site/preview-pc/",
    "/site/preview-724/",
    "/site/preview-responsive/",
)


def _origin() -> str:
    return request.url_root.rstrip("/")


def install_site_seo_foundation(app) -> None:
    """Install public SEO discovery routes without changing the frozen site UI."""

    @app.get("/robots.txt")
    def licensetown_robots():
        origin = _origin()
        body = "\n".join(
            (
                "User-agent: *",
                "Allow: /site",
                "Disallow: /site/view/",
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
        path = request.path
        if any(path.startswith(prefix) for prefix in NOINDEX_PREFIXES):
            response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response
