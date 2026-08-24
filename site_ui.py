import os
from pathlib import Path

from flask import Blueprint, Response, render_template, send_from_directory, url_for


site_ui = Blueprint("site_ui", __name__)

ROOT = Path(__file__).resolve().parent
PREVIEW_PC_DIR = ROOT / "preview-pc"
PREVIEW_724_DIR = ROOT / "preview-724"
PREVIEW_RESPONSIVE_DIR = ROOT / "preview-responsive"

# Public copy is deliberately centralized so the published figure can be
# updated without editing the page layout.
QUESTION_COUNT_LABEL = os.getenv("SITE_QUESTION_COUNT_LABEL", "1,500問以上収録")


@site_ui.get("/site")
def home():
    return render_template(
        "site/home.html",
        pc_view_url=url_for("site_ui.pc_view"),
        mobile_view_url=url_for("site_ui.mobile_view"),
    )


def _preview_document(source_path, base_url, extra_stylesheet_url):
    html = source_path.read_text(encoding="utf-8")
    html = html.replace("<head>", f'<head><base href="{base_url}">', 1)
    html = html.replace(
        "</head>",
        f'<link rel="stylesheet" href="{extra_stylesheet_url}"></head>',
        1,
    )
    return Response(html, mimetype="text/html")


@site_ui.get("/site/view/pc")
def pc_view():
    return _preview_document(
        PREVIEW_PC_DIR / "index.html",
        "/site/preview-pc/",
        "/site/preview-responsive/middle.css",
    )


@site_ui.get("/site/view/mobile")
def mobile_view():
    return _preview_document(
        PREVIEW_724_DIR / "index.html",
        "/site/preview-724/",
        "/site/preview-responsive/mobile.css",
    )


@site_ui.get("/site/source/pc")
def pc_source():
    return send_from_directory(PREVIEW_PC_DIR, "index.html")


@site_ui.get("/site/source/mobile")
def mobile_source():
    return send_from_directory(PREVIEW_724_DIR, "index.html")


@site_ui.get("/site/preview-pc/<path:filename>")
def pc_asset(filename):
    return send_from_directory(PREVIEW_PC_DIR, filename)


@site_ui.get("/site/preview-724/<path:filename>")
def mobile_asset(filename):
    return send_from_directory(PREVIEW_724_DIR, filename)


@site_ui.get("/site/preview-responsive/<path:filename>")
def responsive_asset(filename):
    return send_from_directory(PREVIEW_RESPONSIVE_DIR, filename)
