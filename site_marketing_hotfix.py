from __future__ import annotations

import re
from html import escape

from flask import Response, request

from site_marketing_refresh import FAQ_ITEMS, FAQ_PREVIEW_ITEMS, _onboarding_url


def _preview_items_html() -> str:
    return "".join(
        '<article class="marketing-faq-preview-item">'
        f'<h3>{escape(question)}</h3>'
        f'<p>{escape(answer)}</p>'
        '</article>'
        for question, answer in FAQ_PREVIEW_ITEMS
    )


def _full_faq_page() -> str:
    items = "".join(
        '<article class="faq-item">'
        f'<h2>{escape(question)}</h2>'
        f'<p>{escape(answer)}</p>'
        '</article>'
        for question, answer in FAQ_ITEMS
    )
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>よくある質問 | LicenseTown</title>
<style>
:root{{--green:#087d2d;--ink:#172019;--line:#dbe6dd;--soft:#f7fbf7}}
*{{box-sizing:border-box}}body{{margin:0;background:#f5f7f5;color:var(--ink);font-family:"Yu Gothic","Hiragino Kaku Gothic ProN",Meiryo,sans-serif}}
.wrap{{width:min(960px,calc(100% - 28px));margin:30px auto 56px}}
.top{{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:16px}}.back{{color:var(--green);font-weight:700;text-decoration:none}}
.card{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:30px 34px;box-shadow:0 6px 24px rgba(30,60,40,.06)}}
h1{{margin:0;font-size:30px;color:#173d24}}.lead{{margin:8px 0 22px;color:#59655d;line-height:1.75}}
.faq-item{{padding:18px 2px;border-top:1px solid var(--line)}}.faq-item:last-child{{border-bottom:1px solid var(--line)}}.faq-item h2{{margin:0 0 8px;font-size:17px;line-height:1.55;color:#173d24}}.faq-item p{{margin:0;color:#435047;line-height:1.85;font-size:14px}}
.contact{{margin:26px 0 0;padding:18px 20px;border-radius:10px;background:var(--soft);text-align:center}}.contact a{{color:var(--green);font-weight:700;text-decoration:none}}
@media(max-width:640px){{.wrap{{margin-top:16px}}.card{{padding:22px 18px}}h1{{font-size:24px}}.faq-item{{padding:16px 0}}.faq-item h2{{font-size:15px}}.faq-item p{{font-size:13px}}}}
</style>
</head>
<body><main class="wrap"><div class="top"><a class="back" href="/site/view/pc">← LicenseTownへ戻る</a></div><section class="card"><h1>よくある質問</h1><p class="lead">LicenseTownを始める前によくある質問を、回答までまとめて確認できます。</p>{items}<p class="contact">解決しない場合は <a href="/site/legal/contact">お問い合わせください　›</a></p></section></main></body>
</html>"""


def _line_start_page() -> str:
    target = _onboarding_url()
    if target:
        escaped_target = escape(target, quote=True)
        action = f'<a class="line-button" href="{escaped_target}" target="_blank" rel="noopener noreferrer">LINEを開いて始める　›</a>'
        help_text = "スマホの方は上のボタンからLINEを開けます。PCの方はQRコードをスマホで読み取ってください。"
        qr = '<img src="/site/line-qr.svg" alt="LicenseTownをLINEで始めるQRコード">'
    else:
        action = '<a class="line-button" href="/site/legal/contact">利用開始について問い合わせる　›</a>'
        help_text = "LINEの利用開始リンクを準備中です。"
        qr = ""
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LINEで始める | LicenseTown</title>
<style>:root{{--green:#078329;--ink:#172019;--line:#dbe6dd}}*{{box-sizing:border-box}}body{{margin:0;background:#f6f8f6;color:var(--ink);font-family:"Yu Gothic","Hiragino Kaku Gothic ProN",Meiryo,sans-serif}}.wrap{{width:min(680px,calc(100% - 28px));margin:36px auto}}.card{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:32px;text-align:center;box-shadow:0 6px 24px rgba(30,60,40,.06)}}h1{{margin:0 0 8px;color:var(--green);font-size:28px}}p{{line-height:1.75}}img{{width:180px;height:180px;padding:8px;border:1px solid var(--line);border-radius:12px;background:#fff;object-fit:contain}}.line-button{{display:block;max-width:360px;margin:18px auto 8px;padding:14px 18px;border-radius:10px;background:var(--green);color:#fff;text-decoration:none;font-weight:800}}.help{{color:#58635c;font-size:13px}}.back{{display:inline-block;margin-top:18px;color:var(--green);font-weight:700;text-decoration:none}}@media(max-width:640px){{.wrap{{margin-top:18px}}.card{{padding:24px 18px}}h1{{font-size:23px}}img{{width:150px;height:150px}}}}</style></head>
<body><main class="wrap"><section class="card"><h1>LINEで無料ではじめる</h1><p>LicenseTownは現在、検証期間中のため無料で利用できます。</p>{qr}{action}<p class="help">{help_text}</p><a class="back" href="/site/view/pc">← HPへ戻る</a></section></main></body></html>"""


def _apply_public_hotfix(html: str) -> str:
    preview = _preview_items_html()
    html = re.sub(
        r'<div class="marketing-faq-list">.*?</div>\s*<a class="marketing-contact-link" href="/site/faq">',
        f'<div class="marketing-faq-list marketing-faq-static">{preview}</div><a class="marketing-contact-link" href="/site/faq-all">',
        html,
        count=1,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'<a class="marketing-line-button" href="[^"]*">LINEで無料ではじめる　›</a>',
        '<a class="marketing-line-button" href="/site/line-start">LINEで無料ではじめる　›</a>',
        html,
        count=1,
    )
    styles = """<style id="marketing-hotfix-v03">
.marketing-faq-panel{overflow:hidden!important}
.marketing-faq-static{display:block!important;margin-top:2px!important}
.marketing-faq-preview-item{border-top:1px solid #d8e6da!important;padding:8px 0 7px!important}
.marketing-faq-preview-item:last-child{border-bottom:1px solid #d8e6da!important}
.marketing-faq-preview-item h3{margin:0 0 4px!important;color:#173d24!important;font-size:11px!important;line-height:1.4!important}
.marketing-faq-preview-item p{margin:0!important;color:#435047!important;font-size:9px!important;line-height:1.45!important;display:-webkit-box!important;-webkit-line-clamp:3!important;-webkit-box-orient:vertical!important;overflow:hidden!important}
.marketing-faq-panel .marketing-contact-link{margin-top:9px!important}
.marketing-faq-card .marketing-faq-static{min-height:0!important}
.marketing-faq-card .marketing-faq-preview-item{padding:5px 10px!important}
.marketing-faq-card .marketing-faq-preview-item h3{font-size:9px!important;line-height:1.35!important}
.marketing-faq-card .marketing-faq-preview-item p{font-size:8px!important;line-height:12px!important;-webkit-line-clamp:2!important}
</style>"""
    if 'id="marketing-hotfix-v03"' not in html:
        html = html.replace("</head>", styles + "</head>", 1)
    return html


def install_site_marketing_hotfix(app) -> None:
    @app.get("/site/faq-all")
    def site_faq_all():
        return Response(_full_faq_page(), mimetype="text/html")

    @app.get("/site/line-start")
    def site_line_start():
        return Response(_line_start_page(), mimetype="text/html")

    @app.after_request
    def apply_site_marketing_hotfix(response):
        if response.status_code != 200 or response.mimetype != "text/html" or response.direct_passthrough:
            return response
        if request.path not in {"/site/view/pc", "/site/view/mobile"}:
            return response
        html = response.get_data(as_text=True)
        response.set_data(_apply_public_hotfix(html))
        response.headers["Content-Length"] = str(len(response.get_data()))
        return response
