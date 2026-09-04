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


def _sale_safe_html(html: str) -> str:
    """Remove prototype claims that must not appear as factual sale copy yet.

    This is intentionally a presentation boundary only. The original preview
    assets remain available for design regression, while the public rendered
    views cannot advertise stale counts, a nonexistent free period, or demo
    dashboard values without an explicit image label.
    """
    stats = (
        '<section class="stats"><div class="container"><div><i>▰</i><span><small>新規問題</small>'
        '<b>1000<em>問</em></b></span></div><div><i>▤</i><span><small>過去問</small>'
        '<b>1000<em>問</em></b></span></div><div><i>▥</i><span><small>合計</small>'
        '<b>2000<em>問収録</em></b></span></div></div></section>'
    )
    safe_stats = (
        '<section class="stats"><div class="container"><div><i>▥</i><span>'
        f'<small>問題演習</small><b>{QUESTION_COUNT_LABEL}</b>'
        '</span></div></div></section>'
    )
    html = html.replace(stats, safe_stats)
    html = html.replace('<li>現在無料</li>', '<li>提供条件を準備中</li>')
    html = html.replace('無料期間実施中！', '料金・提供条件は公開準備中')
    html = html.replace(
        'すべての機能を無料で体験できます。',
        '正式な料金・無料範囲は公開前にこのページで案内します。',
    )
    html = html.replace(
        '金融内容（個別のやり取り）は共有されません。',
        '相談内容（個別のやり取り）は共有されません。',
    )
    html = html.replace('総合達成度</small>', '総合達成度 <em>（画面イメージ）</em></small>')
    html = html.replace('合格まで あと <b>123</b>日', '学習ナビ <em>（画面イメージ）</em>')
    return html


def _preview_document(source_path, base_url, extra_stylesheet_url):
    html = source_path.read_text(encoding="utf-8")
    html = _sale_safe_html(html)
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


# ``app.py`` already registers site_ui. Attach small auxiliary boundaries here
# so the Flask entrypoint remains unchanged while their logic stays isolated.
from developer_ui import register_developer_routes
from stripe_billing_ui import stripe_billing_ui
from stripe_webhook_ui import stripe_webhook_ui

register_developer_routes(site_ui)
site_ui.register_blueprint(stripe_billing_ui)
site_ui.register_blueprint(stripe_webhook_ui)
