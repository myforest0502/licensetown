from __future__ import annotations

import io
import os
import re
from html import escape
from urllib.parse import urlparse

import qrcode
import qrcode.image.svg
from flask import Response, abort, request


FAQ_ITEMS = (
    (
        "LicenseTownはどんなサービスですか？",
        "理学療法士国家試験に向けて、問題演習・苦手の整理・復習・次にやる学習の提案までを、LINEを中心に行う伴走型の学習サービスです。",
    ),
    (
        "現在、料金はかかりますか？",
        "現在は検証期間中のため、利用料金はいただいていません。実際に使っていただきながら改善を続けています。",
    ),
    (
        "あとから勝手に料金が発生することはありますか？",
        "ありません。将来、有料化する場合は事前にHPなどでお知らせします。知らないうちに料金が発生することはありません。",
    ),
    (
        "どうやって始めますか？",
        "HPのQRコード、または「LINEで無料ではじめる」ボタンからLicenseTownのLINEを開き、そのまま始められます。",
    ),
    (
        "会員登録やパスワードは必要ですか？",
        "現在、HP上での会員登録やパスワード作成は必要ありません。LINEが学習の入口になります。",
    ),
    (
        "どんな問題が出ますか？",
        "理学療法士国家試験に必要な基礎・専門基礎・専門分野の問題を収録しています。過去問とLicenseTown独自問題を使って学習します。",
    ),
    (
        "普通の問題集と何が違うんですか？",
        "問題を解いて終わりではなく、回答結果や自信度などから、苦手や確認が必要な内容を整理し、次の学習につなげるところが特徴です。",
    ),
    (
        "間違えた問題はどうなりますか？",
        "間違えた内容を記録し、必要に応じて関連する別問題などで理解できたかを確認していきます。",
    ),
    (
        "「合格への道」とは何ですか？",
        "学習履歴から現在の状況を整理し、次に取り組む内容を確認するための画面です。合格を保証したり、合格確率を表示したりするものではありません。",
    ),
    (
        "「教えて源さん」では何ができますか？",
        "国試で分からない用語を入力すると、LicenseTownに保存されている正式な問題・解説をもとに、意味・国試で押さえるポイント・関連問題を確認できます。",
    ),
)

FAQ_PREVIEW_ITEMS = FAQ_ITEMS[:3]


def _onboarding_url() -> str | None:
    candidate = os.getenv("SITE_ONBOARDING_URL", "").strip()
    parsed = urlparse(candidate)
    if parsed.scheme == "https" and parsed.netloc:
        return candidate
    return None


def _faq_details(items=FAQ_ITEMS) -> str:
    return "".join(
        '<details><summary>{}</summary><p class="faq-answer">{}</p></details>'.format(
            escape(question), escape(answer)
        )
        for question, answer in items
    )


def _replace_login(html: str) -> str:
    html = html.replace('<a class="btn login">ログイン</a>', "")
    html = html.replace(
        '<span class="btn login public-static-control" aria-disabled="true">ログイン（準備中）</span>',
        "",
    )
    return html


def _replace_pc_brand(html: str) -> str:
    replacement = (
        '<article class="brand-panel marketing-brand-panel">'
        '<h2>ライセンスタウンは、あなたの「合格したい」を応援します。</h2>'
        '<p class="marketing-brand-lead">理学療法士国家試験の学習を支える伴走型学習サービス</p>'
        '<p class="marketing-brand-copy">問題を解くだけで終わらせず、苦手を整理し、次にやることまでつなげる。'
        '毎日の小さな学習を、合格へ向かう積み重ねに変えていきます。</p>'
        '<div class="marketing-brand-values">'
        '<span>▣<b>国試に特化した<br>豊富な問題</b></span>'
        '<span>◉<b>苦手を整理する<br>学習サポート</b></span>'
        '<span>✓<b>続けやすい<br>学習設計</b></span>'
        '<span>♜<b>本人と家族を<br>支える見守り</b></span>'
        '</div>'
        '<small>迷ったときに「次に何をやるか」がわかる場所を目指しています。</small>'
        '</article>'
    )
    return re.sub(
        r'<article class="brand-panel">.*?</article>',
        replacement,
        html,
        count=1,
        flags=re.DOTALL,
    )


def _replace_pc_faq(html: str) -> str:
    replacement = (
        '<article class="faq-panel marketing-faq-panel" id="faq">'
        '<h2>よくある質問</h2>'
        f'<div class="marketing-faq-list">{_faq_details(FAQ_PREVIEW_ITEMS)}</div>'
        '<a class="marketing-contact-link" href="/site/faq">その他の質問はこちら　›</a>'
        '</article>'
    )
    return re.sub(
        r'<article class="faq-panel(?: marketing-faq-panel)?" id="faq">.*?</article>',
        replacement,
        html,
        count=1,
        flags=re.DOTALL,
    )


def _replace_mobile_faq(html: str) -> str:
    replacement = (
        '<article class="faq-card marketing-faq-card">'
        '<h2>よくあるご質問</h2>'
        f'<div class="faq-list marketing-faq-list">{_faq_details(FAQ_PREVIEW_ITEMS)}</div>'
        '<a class="marketing-contact-link" href="/site/faq">その他の質問はこちら　›</a>'
        '</article>'
    )
    return re.sub(
        r'<article class="faq-card(?: marketing-faq-card)?">.*?</article>',
        replacement,
        html,
        count=1,
        flags=re.DOTALL,
    )


def _cta_contents() -> str:
    target = _onboarding_url()
    if target:
        escaped_target = escape(target, quote=True)
        qr = '<img class="marketing-line-qr" src="/site/line-qr.svg" alt="LicenseTownをLINEで始めるQRコード">'
        button = f'<a class="marketing-line-button" href="{escaped_target}">LINEで無料ではじめる　›</a>'
        desktop_help = '<p class="marketing-qr-help">PCの方は、QRコードをスマホで読み取ってください。</p>'
    else:
        qr = ""
        button = '<a class="marketing-line-button" href="/site/legal/contact">利用開始について問い合わせる　›</a>'
        desktop_help = '<p class="marketing-qr-help">LINEの利用開始リンクを準備中です。</p>'
    return (
        '<h2>検証期間中 無料公開</h2>'
        '<p class="marketing-free-copy">LicenseTownは現在、実際に使っていただきながら改善を続けています。<br>'
        '検証期間中は利用料金をいただいていません。</p>'
        '<p class="marketing-line-copy"><strong>LINEですぐに始められます。</strong></p>'
        f'<div class="marketing-line-start">{qr}<div>{button}{desktop_help}</div></div>'
        '<small class="marketing-free-note">※将来、有料化する場合は事前にHPなどでお知らせします。'
        '知らないうちに料金が発生することはありません。</small>'
    )


def _replace_pc_cta(html: str) -> str:
    replacement = f'<article class="try-panel marketing-free-panel" id="try">{_cta_contents()}</article>'
    return re.sub(
        r'<article class="try-panel(?: marketing-free-panel)?" id="try">.*?</article>',
        replacement,
        html,
        count=1,
        flags=re.DOTALL,
    )


def _replace_mobile_cta(html: str) -> str:
    replacement = (
        '<section class="final-cta" id="try">'
        '<div class="marketing-mobile-free">'
        f'<div class="marketing-mobile-free-inner">{_cta_contents()}</div>'
        '</div></section>'
    )
    return re.sub(
        r'<section class="final-cta" id="try">.*?</section>',
        replacement,
        html,
        count=1,
        flags=re.DOTALL,
    )


def _marketing_styles() -> str:
    return """<style id="marketing-refresh-v02">
.header-actions .btn.primary{margin-left:auto}
.bottom{height:370px!important;padding-top:18px!important;overflow:visible!important}
.bottom-grid{align-items:stretch!important;grid-template-columns:1.35fr .9fr 1.05fr!important;gap:16px!important}
.bottom-grid>.marketing-brand-panel,.marketing-faq-panel,.marketing-free-panel{height:330px!important;min-height:330px!important}
.marketing-brand-panel{padding:24px 24px 18px!important;text-align:center!important;overflow:hidden!important}
.marketing-brand-panel h2{margin:0!important;font-size:20px!important;line-height:1.45!important}
.marketing-brand-lead{margin:8px 0 0!important;color:#1681d4!important;font-size:13px!important}
.marketing-brand-copy{max-width:560px;margin:18px auto 0!important;color:#34443a!important;font-size:13px!important;line-height:1.8!important}
.marketing-brand-values{display:grid!important;grid-template-columns:repeat(4,1fr)!important;gap:10px!important;margin:20px 0 0!important}
.marketing-brand-values span{display:flex!important;align-items:center!important;justify-content:center!important;gap:8px!important;min-height:72px!important;border:1px solid #dce8de!important;border-radius:9px!important;background:#f8fbf8!important;color:#078329!important;font-size:24px!important}
.marketing-brand-values b{color:#233128!important;font-size:11px!important;line-height:1.55!important;text-align:left!important}
.marketing-brand-panel small{display:block!important;margin-top:15px!important;color:#5b675f!important;font-size:11px!important}
.marketing-faq-panel{padding:22px 18px!important;overflow:hidden!important}
.marketing-faq-panel h2{margin:0 0 12px!important;font-size:20px!important}
.marketing-faq-list{display:flex;flex-direction:column;gap:0;margin-top:4px}
.marketing-faq-list details{border-top:1px solid #d8e6da;padding:10px 0}
.marketing-faq-list details:last-child{border-bottom:1px solid #d8e6da}
.marketing-faq-list summary{cursor:pointer;font-weight:700;line-height:1.45;color:#173d24;list-style:none;padding-right:22px;position:relative;font-size:12px}
.marketing-faq-list summary::-webkit-details-marker{display:none}
.marketing-faq-list summary::after{content:'＋';position:absolute;right:2px;top:0;color:#078329;font-weight:700}
.marketing-faq-list details[open] summary::after{content:'－'}
.marketing-faq-list .faq-answer{margin:8px 0 2px!important;line-height:1.6!important;color:#37473d!important;font-size:11px!important;height:auto!important;padding:0 4px!important}
.marketing-contact-link{display:inline-block!important;margin-top:14px!important;color:#087d2d!important;font-weight:700!important;text-decoration:none!important;font-size:12px!important}
.marketing-free-panel{text-align:center!important;padding:22px 16px!important;box-sizing:border-box!important;overflow:hidden!important;background:#fafcf9!important}
.marketing-free-panel h2,.marketing-mobile-free h2{color:#087d2d!important;margin:0 0 8px!important}
.marketing-free-copy{line-height:1.65!important;margin:0 auto 5px!important;max-width:540px!important;font-size:13px!important}
.marketing-line-copy{margin:7px 0 8px!important}
.marketing-line-start{display:flex;align-items:center;justify-content:center;gap:14px;margin:8px auto!important}
.marketing-line-qr{width:100px!important;height:100px!important;background:#fff;padding:5px;border:1px solid #d8e6da;border-radius:8px;box-sizing:border-box;object-fit:contain}
.marketing-line-button{display:inline-block!important;background:#078329!important;color:#fff!important;border-radius:8px!important;padding:11px 16px!important;text-decoration:none!important;font-weight:700!important}
.marketing-qr-help{font-size:10px!important;line-height:1.45!important;margin:7px 0 0!important;color:#57645b!important}
.marketing-free-note{display:block!important;line-height:1.5!important;margin-top:8px!important;color:#59645d!important;font-size:10px!important}
.page{height:2850px!important}
.story-faq{height:350px!important;overflow:visible!important}
.marketing-faq-card{height:334px!important;overflow:visible!important}
.marketing-faq-card .faq-list{height:auto!important;min-height:190px!important;overflow:visible!important}
.marketing-faq-card .marketing-faq-list details{min-height:46px!important;padding:5px 0!important}
.marketing-faq-card .marketing-faq-list summary{font-size:10px!important;padding:8px 28px 8px 10px!important}
.marketing-faq-card .marketing-faq-list .faq-answer{font-size:8px!important;line-height:13px!important;padding:0 28px 8px 10px!important}
.marketing-faq-card>.marketing-contact-link{position:absolute;left:26px;bottom:12px;margin:0!important;font-size:9px!important}
.final-cta{height:360px!important;background:#f7fbf7!important;overflow:visible!important}
.marketing-mobile-free{height:360px!important;padding:20px 36px!important;background:#f7fbf7!important;box-sizing:border-box!important}
.marketing-mobile-free-inner{background:#fff;border:1px solid #d8e6da;border-radius:18px;padding:20px 24px;text-align:center;min-height:320px}
.marketing-mobile-free .marketing-line-start{flex-direction:column;gap:7px!important}
.marketing-mobile-free .marketing-line-qr{width:124px!important;height:124px!important}
.marketing-mobile-free .marketing-line-button{font-size:15px!important;padding:12px 20px!important}
.marketing-mobile-free .marketing-free-copy{font-size:10px!important;line-height:16px!important}
.marketing-mobile-free .marketing-line-copy{font-size:11px!important}
.marketing-mobile-free .marketing-free-note{font-size:8px!important;line-height:12px!important}
@media(max-width:760px){.marketing-line-start{flex-direction:column}.marketing-qr-help{display:none}.marketing-free-copy br{display:none}}
</style>"""


def _faq_page() -> str:
    items = _faq_details(FAQ_ITEMS)
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>よくある質問 | LicenseTown</title>
<style>
:root{{--green:#087d2d;--ink:#172019;--line:#dbe6dd;--soft:#f7fbf7}}
*{{box-sizing:border-box}}body{{margin:0;background:#f6f8f6;color:var(--ink);font-family:"Yu Gothic","Hiragino Kaku Gothic ProN",Meiryo,sans-serif}}
.wrap{{width:min(920px,calc(100% - 32px));margin:42px auto 64px}}.back{{display:inline-block;margin-bottom:18px;color:var(--green);font-weight:700;text-decoration:none}}
.card{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:34px 38px;box-shadow:0 4px 18px rgba(30,60,40,.05)}}
h1{{margin:0;color:#173d24;font-size:30px}}.lead{{margin:10px 0 26px;color:#59655d;line-height:1.7}}
details{{border-top:1px solid var(--line);padding:17px 2px}}details:last-of-type{{border-bottom:1px solid var(--line)}}summary{{cursor:pointer;list-style:none;position:relative;padding-right:34px;font-weight:700;line-height:1.6}}summary::-webkit-details-marker{{display:none}}summary:after{{content:'＋';position:absolute;right:4px;color:var(--green)}}details[open] summary:after{{content:'－'}}.faq-answer{{margin:12px 0 2px;padding:0 28px 0 2px;color:#435047;line-height:1.8}}
.contact{{margin:26px 0 0;padding:18px 20px;border-radius:10px;background:var(--soft);text-align:center}}.contact a{{color:var(--green);font-weight:700;text-decoration:none}}
@media(max-width:640px){{.wrap{{margin-top:20px}}.card{{padding:24px 20px}}h1{{font-size:24px}}details{{padding:15px 0}}}}
</style>
</head>
<body><main class="wrap"><a class="back" href="/site">← LicenseTownへ戻る</a><section class="card"><h1>よくある質問</h1><p class="lead">LicenseTownを始める前によくいただく質問をまとめています。</p>{items}<p class="contact">解決しない場合は <a href="/site/legal/contact">お問い合わせください　›</a></p></section></main></body></html>"""


def refresh_public_site_html(html: str, mobile: bool) -> str:
    html = _replace_login(html)
    if not mobile:
        html = _replace_pc_brand(html)
    html = _replace_mobile_faq(html) if mobile else _replace_pc_faq(html)
    html = _replace_mobile_cta(html) if mobile else _replace_pc_cta(html)
    html = html.replace("提供条件を準備中", "検証期間中 無料公開")
    html = html.replace("料金・提供条件は公開準備中", "検証期間中 無料公開")
    html = re.sub(r'<style id="marketing-refresh-v0[12]">.*?</style>', "", html, flags=re.DOTALL)
    html = html.replace("</head>", _marketing_styles() + "</head>", 1)
    return html


def install_site_marketing_refresh(app) -> None:
    @app.get("/site/line-qr.svg")
    def site_line_qr():
        target = _onboarding_url()
        if not target:
            abort(404)
        image = qrcode.make(target, image_factory=qrcode.image.svg.SvgPathImage, box_size=8, border=2)
        buffer = io.BytesIO()
        image.save(buffer)
        return Response(
            buffer.getvalue(),
            mimetype="image/svg+xml",
            headers={"Cache-Control": "public, max-age=3600"},
        )

    @app.get("/site/faq")
    def site_faq():
        return Response(_faq_page(), mimetype="text/html")

    @app.after_request
    def apply_site_marketing_refresh(response):
        if response.status_code != 200 or response.mimetype != "text/html":
            return response
        if response.direct_passthrough:
            return response
        path = request.path
        if path not in {"/site/view/pc", "/site/view/mobile"}:
            return response
        html = response.get_data(as_text=True)
        response.set_data(refresh_public_site_html(html, mobile=path.endswith("/mobile")))
        response.headers["Content-Length"] = str(len(response.get_data()))
        return response
