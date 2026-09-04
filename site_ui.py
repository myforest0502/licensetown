import json
import os
import re
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from flask import Blueprint, Response, render_template, request, send_from_directory, url_for


site_ui = Blueprint("site_ui", __name__)

ROOT = Path(__file__).resolve().parent
PREVIEW_PC_DIR = ROOT / "preview-pc"
PREVIEW_724_DIR = ROOT / "preview-724"
PREVIEW_RESPONSIVE_DIR = ROOT / "preview-responsive"
QUESTION_BANK_PATH = ROOT / "data" / "question_bank" / "questions.json"


def _question_count_label() -> str:
    """Return one factual public question-count label from the formal bank.

    A deliberate environment override remains available for conservative public
    copy, but the default cannot silently drift away from the formal bank.
    """
    override = os.getenv("SITE_QUESTION_COUNT_LABEL", "").strip()
    if override:
        return override
    try:
        payload = json.loads(QUESTION_BANK_PATH.read_text(encoding="utf-8"))
        count = len(payload)
    except (OSError, ValueError, TypeError):
        return "問題を収録"
    return f"{count}問収録"


def _public_onboarding_url() -> str:
    """Return a verified HTTPS onboarding URL or fail closed to contact.

    Public CTA must never guess a LINE destination. Until the operator supplies
    the intended HTTPS onboarding URL, the CTA resolves to LicenseTown contact.
    """
    candidate = os.getenv("SITE_ONBOARDING_URL", "").strip()
    if not candidate:
        return "/site/legal/contact"
    parsed = urlparse(candidate)
    if parsed.scheme != "https" or not parsed.netloc:
        return "/site/legal/contact"
    return candidate


@site_ui.get("/site")
def home():
    return render_template(
        "site/home.html",
        pc_view_url=url_for("site_ui.pc_view"),
        mobile_view_url=url_for("site_ui.mobile_view"),
    )


def _wire_primary_ctas(html: str) -> str:
    target = escape(_public_onboarding_url(), quote=True)

    def replace_anchor(match):
        attrs = match.group("attrs") or ""
        label = match.group("label")
        if re.search(r'\shref="[^"]*"', attrs):
            attrs = re.sub(r'\shref="[^"]*"', f' href="{target}"', attrs, count=1)
        else:
            attrs += f' href="{target}"'
        return f"<a{attrs}>{label}</a>"

    return re.sub(
        r'<a(?P<attrs>[^>]*)>(?P<label>まずは使ってみる(?:　›)?)</a>',
        replace_anchor,
        html,
    )


def _wire_same_document_fragments(html: str) -> str:
    """Keep hash navigation on the rendered preview document, not its asset base.

    The preview documents use ``<base>`` so relative image/CSS paths resolve to
    their asset directories. Without this rewrite, ``href="#faq"`` also resolves
    against that asset base and leaves the public document, which caused the
    observed 403 navigation failures.
    """
    current_path = escape(request.path, quote=True)
    return re.sub(
        r'href="#([A-Za-z0-9_-]+)"',
        lambda match: f'href="{current_path}#{match.group(1)}"',
        html,
    )


def _inject_mobile_faq_answers(html: str) -> str:
    """Turn the frozen mobile FAQ shell into a useful public accordion."""
    if 'class="faq-list"' not in html or 'class="faq-answer"' in html:
        return html

    answers = {
        "料金はかかりますか？": (
            "現在は多くの方に使っていただき、改善する段階です。"
            "月額料金はお願いしていません。正式な料金・提供条件を決める際は、このページでご案内します。"
        ),
        "LINEだけで使えますか？": (
            "学習の中心はLINEで利用できます。合格への道や見守りなど、"
            "一部の画面はブラウザで開いて確認します。"
        ),
        "見守り機能では何が見えますか？": (
            "学習日数、回答数、学習時間、分野別の取り組み状況などを確認できます。"
            "個別の相談内容は共有されません。"
        ),
        "どんな人に向いていますか？": (
            "理学療法士国家試験に向けて、苦手や次にやることを整理しながら学びたい方と、"
            "その学習を見守りたいご家族を想定しています。"
        ),
    }
    for question, answer in answers.items():
        html = html.replace(
            f"<details><summary>{question}</summary></details>",
            f'<details><summary>{question}</summary><p class="faq-answer">{answer}</p></details>',
        )
    return html


def _inject_mobile_trust_support(html: str) -> str:
    """Add the approved trust/support message to the public 724px mobile view.

    The original 724px design source stays frozen. Public rendering receives the
    same operating stance already approved on PC, stacked for the narrow canvas.
    """
    if 'class="section story-faq"' not in html or 'class="mobile-trust-support"' in html:
        return html

    section = (
        '<section class="mobile-trust-support" id="mobile-principles">'
        '<article class="mobile-principles-card">'
        '<span>LicenseTownが大切にしていること</span>'
        '<h2>迷ったときは、「それは誠実か？」で考える。</h2>'
        '<p>LicenseTownは、まだ完成したサービスだとは考えていません。'
        'まずは実際に使っていただき、改善の声を集めながら少しずつ良くしていきます。</p>'
        '<p>十分に胸を張って「料金をいただける」と思えるまでは、月額料金をお願いしません。'
        '学ぶ人に本当に役に立つか、自分の家族にも勧められるか。これからも「誠実」を判断基準にします。</p>'
        '<div class="mobile-principle-points"><b>利益より先に信頼</b><b>売るより先に役に立つ</b><b>胸を張れるものを届ける</b></div>'
        '</article>'
        '<article class="mobile-support-card">'
        '<span>LicenseTownを応援する</span>'
        '<h2>いまは、まず使ってもらい、良くしていく。</h2>'
        '<p>もっとレスポンスを速くしたい。スマホでも、もっと使いやすくしたい。'
        '学習機能や見守り機能も、もっと良くしたい。そのための開発費が必要なのも事実です。</p>'
        '<p>「少し応援してもいいな」と思っていただけたら、100円からの開発支援で応援していただけると嬉しいです。'
        '<strong>支援は完全に任意で、支援の有無で現在の学習機能に差はありません。</strong></p>'
        '<div class="mobile-support-amounts"><b>100円</b><b>300円</b><b>500円</b><b>1,000円</b></div>'
        '<p class="mobile-support-cap">1回あたり1,000円まで。それ以上の金額は、今は受け取りません。'
        'いただいた支援は、LicenseTownの改善・運営・開発のために使います。</p>'
        '<a href="/site/support">開発支援について詳しく見る　›</a>'
        '<small>※現在は支援受付の準備中です。決済機能はまだ公開していません。</small>'
        '</article>'
        '</section>'
    )
    return html.replace('<section class="final-cta"', section + '<section class="final-cta"', 1)


def _add_static_control_class(attrs: str) -> str:
    class_match = re.search(r'class="([^"]*)"', attrs)
    if class_match:
        classes = f'{class_match.group(1)} public-static-control'.strip()
        return attrs[: class_match.start()] + f'class="{classes}"' + attrs[class_match.end() :]
    return attrs + ' class="public-static-control"'


def _make_public_dead_interactions_static(html: str) -> str:
    """Make unavailable public-preview interactions explicitly inert."""
    html = html.replace(
        '<a class="btn login">ログイン</a>',
        '<span class="btn login public-static-control" aria-disabled="true">'
        'ログイン（準備中）</span>',
    )
    html = html.replace(
        '<a class="detail">詳しく見る</a>',
        '<span class="detail public-static-control" aria-disabled="true">'
        '表示イメージ</span>',
    )
    html = html.replace(
        '<a>その他の質問はこちら　›</a>',
        '<a href="/site/legal/contact">その他の質問はこちら　›</a>',
    )

    video_pattern = re.compile(
        r'<button class="video-card"[^>]*>(?P<body>.*?)</button>',
        flags=re.DOTALL,
    )

    def replace_video(match):
        body = match.group("body").replace(
            '<span class="play">▶</span>',
            '<span class="video-status">紹介動画<br>準備中</span>',
        )
        return (
            '<div class="video-card video-card-static" '
            'aria-label="30秒でわかるLicenseTown 紹介動画 準備中">'
            f"{body}</div>"
        )

    html = video_pattern.sub(replace_video, html)

    def replace_href_less_anchor(match):
        attrs = match.group("attrs") or ""
        if re.search(r"\bhref\s*=", attrs, flags=re.IGNORECASE):
            return match.group(0)
        attrs = _add_static_control_class(attrs)
        return f'<span{attrs} aria-disabled="true">{match.group("body")}</span>'

    return re.sub(
        r'<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>',
        replace_href_less_anchor,
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )


def _sale_safe_html(html: str) -> str:
    """Remove prototype claims that must not appear as factual sale copy yet.

    This is intentionally a presentation boundary only. The original preview
    assets remain available for design regression, while the public rendered
    views cannot advertise stale counts, a nonexistent free period, or demo
    dashboard values without an explicit image label.
    """
    count_label = _question_count_label()
    stats = (
        '<section class="stats"><div class="container"><div><i>▰</i><span><small>新規問題</small>'
        '<b>1000<em>問</em></b></span></div><div><i>▤</i><span><small>過去問</small>'
        '<b>1000<em>問</em></b></span></div><div><i>▥</i><span><small>合計</small>'
        '<b>2000<em>問収録</em></b></span></div></div></section>'
    )
    safe_stats = (
        '<section class="stats"><div class="container"><div><i>▥</i><span>'
        f'<small>問題演習</small><b>{count_label}</b>'
        '</span></div></div></section>'
    )
    html = html.replace(stats, safe_stats)
    html = re.sub(
        r'(合計</small><b>)\d+(<em>問収録</em>)',
        lambda match: f"{match.group(1)}{count_label.removesuffix('問収録')}{match.group(2)}"
        if count_label.endswith("問収録") and count_label[:-3].isdigit()
        else f"{match.group(1)}{escape(count_label)}{match.group(2)}",
        html,
    )
    html = html.replace("1,500問以上収録", count_label)
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
    html = html.replace(
        '<a>特定商取引法に基づく表記</a>',
        '<a href="/site/legal/commercial-transactions">特定商取引法に基づく表記</a>',
    )
    html = html.replace(
        '<a>プライバシーポリシー</a>',
        '<a href="/site/legal/privacy">プライバシーポリシー</a>',
    )
    html = html.replace(
        '<a>利用規約</a>',
        '<a href="/site/legal/terms">利用規約</a>',
    )
    html = html.replace(
        '<a>運営会社</a>',
        '<a href="/site/legal/operator">運営者情報</a>',
    )
    html = html.replace(
        '<a>運営情報</a>',
        '<a href="/site/legal/operator">運営情報</a>',
    )
    html = html.replace(
        '<a>お問い合わせ</a>',
        '<a href="/site/legal/contact">お問い合わせ</a><a href="/site/support">LicenseTownを応援する</a>',
    )
    html = _inject_mobile_faq_answers(html)
    html = _inject_mobile_trust_support(html)
    html = _wire_primary_ctas(html)
    return _make_public_dead_interactions_static(html)


def _preview_interaction_script() -> str:
    """Small public-only behaviors for the frozen preview documents."""
    return """<script>
document.addEventListener('DOMContentLoaded', function () {
  var faqItems = document.querySelectorAll('.faq-list details');
  faqItems.forEach(function (item) {
    item.addEventListener('toggle', function () {
      if (!item.open) return;
      faqItems.forEach(function (other) {
        if (other !== item) other.open = false;
      });
    });
  });
});
</script>"""


def _preview_document(source_path, base_url, extra_stylesheet_url):
    html = source_path.read_text(encoding="utf-8")
    html = _sale_safe_html(html)
    html = _wire_same_document_fragments(html)
    html = html.replace("<head>", f'<head><base href="{base_url}">', 1)
    html = html.replace(
        "</head>",
        f'<link rel="stylesheet" href="{extra_stylesheet_url}"></head>',
        1,
    )
    html = html.replace("</body>", _preview_interaction_script() + "</body>", 1)
    return Response(html, mimetype="text/html")


def _sale_safe_source(source_path):
    html = source_path.read_text(encoding="utf-8")
    return Response(_sale_safe_html(html), mimetype="text/html")


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
    return _sale_safe_source(PREVIEW_PC_DIR / "index.html")


@site_ui.get("/site/source/mobile")
def mobile_source():
    return _sale_safe_source(PREVIEW_724_DIR / "index.html")


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
from site_legal_ui import site_legal_ui
from stripe_billing_ui import stripe_billing_ui
from stripe_webhook_ui import stripe_webhook_ui

register_developer_routes(site_ui)
site_ui.register_blueprint(site_legal_ui)
site_ui.register_blueprint(stripe_billing_ui)
site_ui.register_blueprint(stripe_webhook_ui)
