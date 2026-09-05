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
    (
        "親の見守り機能では何が見えますか？",
        "学習した問題数、学習時間、取り組んだ分野など、学習状況を確認できます。本人の個別の相談内容を見せるための機能ではありません。",
    ),
    (
        "不具合や分かりにくいところを見つけたらどうすればいいですか？",
        "ぜひお問い合わせから教えてください。LicenseTownは現在、実際の利用をもとに改善している段階です。いただいた声を今後の改善に活かします。",
    ),
)


def _onboarding_url() -> str | None:
    candidate = os.getenv("SITE_ONBOARDING_URL", "").strip()
    parsed = urlparse(candidate)
    if parsed.scheme == "https" and parsed.netloc:
        return candidate
    return None


def _faq_details() -> str:
    return "".join(
        '<details><summary>{}</summary><p class="faq-answer">{}</p></details>'.format(
            escape(question), escape(answer)
        )
        for question, answer in FAQ_ITEMS
    )


def _replace_login(html: str) -> str:
    html = html.replace('<a class="btn login">ログイン</a>', "")
    html = html.replace(
        '<span class="btn login public-static-control" aria-disabled="true">ログイン（準備中）</span>',
        "",
    )
    return html


def _replace_pc_faq(html: str) -> str:
    replacement = (
        '<article class="faq-panel marketing-faq-panel" id="faq">'
        '<h2>よくある質問</h2>'
        f'<div class="marketing-faq-list">{_faq_details()}</div>'
        '<a class="marketing-contact-link" href="/site/legal/contact">'
        '解決しない場合はお問い合わせください　›</a>'
        '</article>'
    )
    return re.sub(
        r'<article class="faq-panel" id="faq">.*?</article>',
        replacement,
        html,
        count=1,
        flags=re.DOTALL,
    )


def _replace_mobile_faq(html: str) -> str:
    replacement = (
        '<article class="faq-card marketing-faq-card">'
        '<h2>よくあるご質問</h2>'
        f'<div class="faq-list marketing-faq-list">{_faq_details()}</div>'
        '<a class="marketing-contact-link" href="/site/legal/contact">'
        '解決しない場合はお問い合わせください　›</a>'
        '</article>'
    )
    return re.sub(
        r'<article class="faq-card">.*?</article>',
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
        r'<article class="try-panel" id="try">.*?</article>',
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
    return """<style id="marketing-refresh-v01">
.header-actions .btn.primary{margin-left:auto}
.bottom{height:580px!important;padding-top:16px!important;overflow:visible!important}
.bottom-grid{align-items:stretch!important}
.bottom-grid>.brand-panel,.marketing-faq-panel,.marketing-free-panel{height:540px!important;min-height:540px!important}
.marketing-faq-panel{padding:18px!important;overflow:auto!important}
.marketing-faq-list{display:flex;flex-direction:column;gap:0;margin-top:8px}
.marketing-faq-list details{border-top:1px solid #d8e6da;padding:7px 0}
.marketing-faq-list details:last-child{border-bottom:1px solid #d8e6da}
.marketing-faq-list summary{cursor:pointer;font-weight:700;line-height:1.45;color:#173d24;list-style:none;padding-right:22px;position:relative;font-size:12px}
.marketing-faq-list summary::-webkit-details-marker{display:none}
.marketing-faq-list summary::after{content:'＋';position:absolute;right:2px;top:0;color:#078329;font-weight:700}
.marketing-faq-list details[open] summary::after{content:'－'}
.marketing-faq-list .faq-answer{margin:8px 0 2px!important;line-height:1.6!important;color:#37473d!important;font-size:12px!important;height:auto!important;padding:0 4px!important}
.marketing-contact-link{display:inline-block!important;margin-top:12px!important;color:#087d2d!important;font-weight:700!important;text-decoration:none!important}
.marketing-free-panel{text-align:center!important;padding:28px 18px!important;box-sizing:border-box!important;overflow:visible!important}
.marketing-free-panel h2,.marketing-mobile-free h2{color:#087d2d!important;margin:0 0 10px!important}
.marketing-free-copy{line-height:1.7!important;margin:0 auto 8px!important;max-width:540px!important}
.marketing-line-copy{margin:8px 0 12px!important}
.marketing-line-start{display:flex;align-items:center;justify-content:center;gap:16px;margin:10px auto!important}
.marketing-line-qr{width:112px!important;height:112px!important;background:#fff;padding:6px;border:1px solid #d8e6da;border-radius:8px;box-sizing:border-box;object-fit:contain}
.marketing-line-button{display:inline-block!important;background:#078329!important;color:#fff!important;border-radius:8px!important;padding:12px 18px!important;text-decoration:none!important;font-weight:700!important}
.marketing-qr-help{font-size:12px!important;line-height:1.5!important;margin:8px 0 0!important;color:#57645b!important}
.marketing-free-note{display:block!important;line-height:1.55!important;margin-top:12px!important;color:#59645d!important}
.page{height:3500px!important}
.story-faq{height:696px!important;overflow:visible!important}
.marketing-faq-card{height:680px!important;overflow:visible!important}
.marketing-faq-card .faq-list{height:auto!important;min-height:500px!important;overflow:visible!important}
.marketing-faq-card .marketing-faq-list details{min-height:38px!important;padding:5px 0!important}
.marketing-faq-card .marketing-faq-list summary{font-size:10px!important;padding:8px 28px 8px 10px!important}
.marketing-faq-card .marketing-faq-list .faq-answer{font-size:8px!important;line-height:13px!important;padding:0 28px 8px 10px!important}
.marketing-faq-card>.marketing-contact-link{position:absolute;left:26px;bottom:12px;margin:0!important;font-size:9px!important}
.final-cta{height:390px!important;background:#f7fbf7!important;overflow:visible!important}
.marketing-mobile-free{height:390px!important;padding:24px 36px!important;background:#f7fbf7!important;box-sizing:border-box!important}
.marketing-mobile-free-inner{background:#fff;border:1px solid #d8e6da;border-radius:18px;padding:22px 24px;text-align:center;min-height:340px}
.marketing-mobile-free .marketing-line-start{flex-direction:column;gap:8px!important}
.marketing-mobile-free .marketing-line-qr{width:132px!important;height:132px!important}
.marketing-mobile-free .marketing-line-button{font-size:15px!important;padding:12px 20px!important}
.marketing-mobile-free .marketing-free-copy{font-size:10px!important;line-height:16px!important}
.marketing-mobile-free .marketing-line-copy{font-size:11px!important}
.marketing-mobile-free .marketing-free-note{font-size:8px!important;line-height:12px!important}
@media(max-width:760px){.marketing-line-start{flex-direction:column}.marketing-qr-help{display:none}.marketing-free-copy br{display:none}}
</style>"""


def refresh_public_site_html(html: str, mobile: bool) -> str:
    html = _replace_login(html)
    html = _replace_mobile_faq(html) if mobile else _replace_pc_faq(html)
    html = _replace_mobile_cta(html) if mobile else _replace_pc_cta(html)
    html = html.replace("提供条件を準備中", "検証期間中 無料公開")
    html = html.replace("料金・提供条件は公開準備中", "検証期間中 無料公開")
    if 'id="marketing-refresh-v01"' not in html:
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
