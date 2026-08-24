import os
from pathlib import Path

from flask import Blueprint, render_template, send_from_directory


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
        pc_source_url="/site/source/pc",
        mobile_source_url="/site/source/mobile",
        pc_base_url="/site/preview-pc/",
        mobile_base_url="/site/preview-724/",
        middle_css_url="/site/preview-responsive/middle.css",
        mobile_css_url="/site/preview-responsive/mobile.css",
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
