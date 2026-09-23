from __future__ import annotations

import io
import json
import os
import re
from html import escape
from pathlib import Path
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
        "正式公開前の無料モニターとして、先着30名まで月額料金なしでご利用いただけます。30名に達した時点で、新規受付を終了します。",
    ),
    (
        "あとから勝手に料金が発生することはありますか？",
        "ありません。将来、有料化する場合は事前にHPなどでお知らせします。知らないうちに料金が発生することはありません。",
    ),
    (
        "どうやって始めますか？",
        "HPのQRコード、または「LINEで無料βを始める」ボタンからLicenseTownのLINEを開き、そのまま始められます。",
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
        button = f'<a class="marketing-line-button" href="{escaped_target}">LINEで無料βを始める　›</a>'
        desktop_help = '<p class="marketing-qr-help">PCの方は、QRコードをスマホで読み取ってください。</p>'
    else:
        qr = ""
        button = '<a class="marketing-line-button" href="/site/legal/contact">利用開始について問い合わせる　›</a>'
        desktop_help = '<p class="marketing-qr-help">LINEの利用開始リンクを準備中です。</p>'
    return (
        '<h2>無料モニター 先着30名限定</h2>'
        '<p class="marketing-free-copy">正式公開前の無料モニターとして、先着30名まで月額料金なしでご利用いただけます。<br>'
        '実際に使っていただきながら、学習に役立つサービスへ改善していきます。</p>'
        '<p class="marketing-line-copy"><strong>LINEですぐに始められます。</strong></p>'
        f'<div class="marketing-line-start">{qr}<div>{button}{desktop_help}</div></div>'
        '<small class="marketing-free-note">※30名に達した時点で、新規の無料モニター受付を終了します。'
        '将来、料金が発生する場合は事前にご案内します。</small>'
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



QUESTION_BANK_PATH = Path(__file__).resolve().parents[1] / "pt" / "data" / "question_bank" / "questions.json"


def _mobile_formal_counts() -> tuple[int, int, int]:
    try:
        rows = json.loads(QUESTION_BANK_PATH.read_text(encoding="utf-8"))
        original = sum(row.get("source") == "O" for row in rows)
        past_exam = sum(row.get("source") == "P" for row in rows)
        return original, past_exam, len(rows)
    except (OSError, ValueError, TypeError):
        return 1643, 1100, 2743


def _prepare_mobile_layout(html: str) -> str:
    """Convert the frozen 724px public view into a real narrow-screen flow."""
    html = html.replace(
        '<meta name="viewport" content="width=724, initial-scale=1">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        1,
    )
    html = html.replace(
        '<section class="section road">',
        '<section class="section road" id="road">',
        1,
    )
    html = re.sub(
        r'<p>問題演習・弱点分析・学習提案を通して、<br>'
        r'「じゃあ、今何をやるべきか」を一緒に考え、<br>'
        r'資格取得までの努力を結果につなげる伴走型学習サービス。</p>',
        '<p>豊富な問題演習と、弱点分析、学習ナビゲートで<br>'
        'あなたの合格を、LicenseTownが支えます。</p>',
        html,
        count=1,
    )
    if 'class="mobile-hero-actions"' not in html:
        target = _onboarding_url() or "/site/legal/contact"
        actions = (
            '<div class="mobile-hero-actions">'
            f'<a class="mobile-hero-primary" href="{escape(target, quote=True)}" '
            'target="_blank" rel="noopener noreferrer">LINEで無料βを始める</a>'
            '<a class="mobile-hero-secondary" href="#road">合格への道を見る</a>'
            '</div>'
        )
        html = html.replace('</div>\n        <img class="hero-visual"', actions + '</div>\n        <img class="hero-visual"', 1)

    original, past_exam, total = _mobile_formal_counts()
    if 'class="mobile-question-stats"' not in html:
        stats = (
            '<section class="mobile-question-stats" aria-label="収録問題数">'
            f'<div><small>新規問題</small><b>{original}<em>問</em></b></div>'
            f'<div><small>過去問</small><b>{past_exam}<em>問</em></b></div>'
            f'<div class="total"><small>合計</small><b>{total}<em>問</em></b></div>'
            '</section>'
        )
        html = html.replace(
            '</section>\n\n      <section class="section problems">',
            '</section>' + stats + '\n\n      <section class="section problems">',
            1,
        )
    return html


def _mobile_responsive_styles() -> str:
    return """<style id="mobile-responsive-overhaul-v01">
html,body{min-width:0!important;width:100%!important;overflow-x:hidden!important;background:#fff!important}
body{font-size:16px!important}
.page{width:100%!important;height:auto!important;min-height:0!important;margin:0!important;overflow:visible!important}
.section{width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;padding:34px 18px!important}
.section-no{display:none!important}
.section h2{position:static!important;width:auto!important;transform:none!important;white-space:normal!important;font-size:clamp(24px,7vw,30px)!important;line-height:1.4!important;text-align:left!important}

/* compact mobile header */
.header{position:relative!important;width:100%!important;height:64px!important;padding:0 16px!important;display:flex!important;align-items:center!important;justify-content:space-between!important;background:#fff!important}
.logo{position:static!important;font-size:22px!important;line-height:1!important}
.main-nav{display:none!important}
.header-cta{position:static!important;width:auto!important;height:38px!important;padding:0 13px!important;border-radius:20px!important;font-size:12px!important;white-space:nowrap!important}

/* hero: read top-to-bottom, then act */
.hero{display:flex!important;flex-direction:column!important;padding-top:28px!important;background:#fff!important}
.hero-copy{position:static!important;width:100%!important}
.hero-copy h1{position:static!important;width:auto!important;margin:0!important;font-size:clamp(29px,8vw,38px)!important;line-height:1.35!important;letter-spacing:0!important;white-space:normal!important;transform:none!important}
.hero-copy>p{position:static!important;width:auto!important;margin:16px 0 0!important;font-size:15px!important;line-height:1.8!important;font-weight:500!important}
.hero-copy>p br{display:none!important}
.hero .free-beta-hero-notice{position:static!important;width:100%!important;margin:22px 0 0!important;display:grid!important;grid-template-columns:1fr!important;gap:9px!important}
.hero .free-beta-hero-notice strong,.hero .free-beta-hero-notice span{display:block!important;width:100%!important;max-width:none!important;min-height:0!important;margin:0!important;padding:10px 12px!important;border-radius:12px!important;font-size:14px!important;line-height:1.55!important;text-align:center!important;white-space:normal!important;overflow:visible!important}
.hero .free-beta-hero-notice span{font-size:15px!important;font-weight:800!important}
.mobile-hero-actions{display:grid!important;grid-template-columns:1fr!important;gap:10px!important;margin-top:18px!important}
.mobile-hero-primary,.mobile-hero-secondary{display:flex!important;align-items:center!important;justify-content:center!important;width:100%!important;min-height:50px!important;border-radius:10px!important;font-size:16px!important;font-weight:800!important;text-align:center!important}
.mobile-hero-primary{background:#078329!important;color:#fff!important;box-shadow:0 5px 14px rgba(7,131,41,.18)!important}
.mobile-hero-secondary{border:1px solid #d3ddd5!important;background:#fff!important;color:#425249!important;font-weight:700!important}
.hero .chips{position:static!important;width:100%!important;height:auto!important;margin:18px 0 0!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important;white-space:normal!important}
.hero .chips li{display:flex!important;align-items:center!important;justify-content:center!important;width:100%!important;height:auto!important;min-height:38px!important;padding:7px 8px!important;font-size:13px!important;line-height:1.4!important;text-align:center!important;white-space:normal!important}
.hero .chips li:nth-child(1),.hero .chips li:nth-child(4){display:none!important}
.hero .video-card{display:none!important}
.hero-visual{position:static!important;order:2!important;display:block!important;width:min(72vw,280px)!important;height:auto!important;max-height:none!important;margin:24px auto 0!important;object-fit:contain!important}

/* formal question volume */
.mobile-question-stats{width:100%!important;padding:18px 16px!important;display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:8px!important;border-block:1px solid #e2e7e3!important;background:#f8fbf8!important}
.mobile-question-stats div{min-width:0!important;padding:10px 4px!important;text-align:center!important;border-right:1px solid #dce5de!important}
.mobile-question-stats div:last-child{border-right:0!important}
.mobile-question-stats small{display:block!important;font-size:12px!important;font-weight:700!important;color:#506057!important}
.mobile-question-stats b{display:block!important;margin-top:4px!important;color:#176f50!important;font-size:22px!important;line-height:1.15!important}
.mobile-question-stats em{margin-left:2px!important;color:#334039!important;font-size:12px!important;font-style:normal!important}

/* repeated card families */
.problems>h2,.can-do>h2,.road>h2,.howto>h2,.terakoya>h2,.parents>h2{margin-bottom:22px!important}
.problem-grid,.feature-grid{position:static!important;width:100%!important;height:auto!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:12px!important}
.problem-card,.feature-grid article{position:relative!important;width:100%!important;height:196px!important;min-width:0!important;border-radius:10px!important}
.problem-card>span{left:10px!important;top:10px!important;width:24px!important;height:24px!important;font-size:12px!important}
.problem-card h3{position:static!important;width:auto!important;margin:14px 12px 0!important;padding-left:20px!important;font-size:14px!important;line-height:1.55!important;text-align:center!important}
.problem-card img{bottom:10px!important;max-width:80%!important;height:100px!important;width:auto!important}
.feature-grid img{position:static!important;display:block!important;width:auto!important;height:78px!important;margin:14px auto 8px!important;transform:none!important}
.feature-grid h3{position:static!important;width:auto!important;margin:0 8px!important;font-size:16px!important;line-height:1.4!important}
.feature-grid h3 small{font-size:12px!important}
.feature-grid p{position:static!important;width:auto!important;margin:6px 10px 0!important;font-size:13px!important;line-height:1.45!important}
.feature-grid p br{display:none!important}

/* dashboard becomes a readable stacked preview */
.dashboard-main{position:static!important;width:100%!important;height:auto!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:10px!important;padding:12px!important;overflow:hidden!important}
.dashboard-main .dash-nav{display:none!important}
.dashboard-main .metric,.dashboard-main .progress-card,.dashboard-main .rank-card,.dashboard-main .today-card,.dashboard-main .mentor-card{position:relative!important;left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;width:auto!important;height:auto!important;min-height:120px!important;padding:12px!important;overflow:hidden!important}
.dashboard-main .metric small,.dashboard-main .progress-card>small{font-size:12px!important}
.dashboard-main .metric b{position:static!important;display:block!important;margin-top:14px!important;font-size:28px!important;line-height:1.2!important}
.dashboard-main .metric p{position:static!important;width:auto!important;margin-top:10px!important;font-size:11px!important}
.dashboard-main .pass .ring{display:none!important}
.dashboard-main .progress-card,.dashboard-main .mentor-card{grid-column:1/-1!important}
.dashboard-main .progress-card{min-height:190px!important}
.dashboard-main .bars label{height:24px!important;font-size:11px!important}
.dashboard-main .bars i{flex:1!important;width:auto!important;height:7px!important}
.dashboard-main .bars i:after{height:7px!important}
.dashboard-main .bars b{font-size:10px!important}
.dashboard-main .rank-card h4,.dashboard-main .today-card h4{font-size:14px!important}
.dashboard-main .rank-card li,.dashboard-main .today-card li{height:auto!important;min-height:34px!important;font-size:11px!important;line-height:1.4!important;padding:8px 0!important}
.dashboard-main .public-static-control{font-size:10px!important}
.dashboard-main .mentor-card{display:flex!important;align-items:center!important;gap:14px!important;min-height:130px!important}
.dashboard-main .mentor-image{position:static!important;width:94px!important;height:auto!important}
.dashboard-main .mentor-card p{position:static!important;margin:0!important;font-size:13px!important;line-height:1.6!important}

/* vertical learning flow */
.steps{position:static!important;width:100%!important;height:auto!important;display:flex!important;flex-direction:column!important;align-items:stretch!important;gap:8px!important}
.steps article{width:100%!important;height:auto!important;min-height:150px!important;padding:16px 18px 14px 112px!important;text-align:left!important}
.steps>i{width:100%!important;height:28px!important;line-height:28px!important;transform:rotate(90deg)!important;font-size:24px!important}
.steps article>span{left:12px!important;top:12px!important;width:28px!important;height:28px!important;font-size:13px!important}
.steps img{left:58px!important;top:46px!important;width:70px!important;height:70px!important;transform:translateX(-50%)!important}
.steps h3{position:static!important;width:auto!important;margin:18px 0 0!important;font-size:18px!important;line-height:1.4!important}
.steps p{position:static!important;width:auto!important;margin:8px 0 0!important;font-size:14px!important;line-height:1.6!important}
.steps p br{display:none!important}

/* terakoya: text then illustration */
.tera-body,.terakoya blockquote,.terakoya>img{position:static!important;width:100%!important;height:auto!important}
.tera-body{margin:0!important;font-size:15px!important;line-height:1.9!important;font-weight:500!important}
.tera-body br{display:none!important}
.terakoya blockquote{margin:20px 0!important;padding:18px 22px 18px 48px!important;font-size:14px!important;line-height:1.8!important}
.terakoya>img{display:block!important;max-width:560px!important;margin:18px auto 0!important;object-fit:contain!important}

/* parent view: stack main and supporting evidence */
.parent-board{position:static!important;width:100%!important;height:auto!important;padding:14px!important;display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:8px!important}
.parent-board>strong{position:static!important;grid-column:1/-1!important;font-size:14px!important}
.parent-stat,.parent-stat.s2,.parent-stat.s3{position:relative!important;left:auto!important;top:auto!important;width:auto!important;height:auto!important;min-height:115px!important;padding:16px 6px!important}
.parent-stat small{font-size:11px!important}
.parent-stat b{margin-top:9px!important;font-size:22px!important}
.parent-stat em{font-size:10px!important}
.parent-stat p{margin:10px 0 0!important;font-size:10px!important}
.parent-progress{position:relative!important;left:auto!important;top:auto!important;grid-column:1/-1!important;width:auto!important;height:auto!important;min-height:190px!important;padding:12px!important}
.parent-progress>b{font-size:13px!important}
.parent-progress .bars label{height:25px!important;font-size:11px!important}
.parent-progress .bars i{flex:1!important;width:auto!important;height:7px!important}
.parent-message{position:relative!important;left:auto!important;top:auto!important;grid-column:1/-1!important;width:auto!important;height:auto!important;padding:12px!important;font-size:12px!important;line-height:1.65!important}
.parent-list{position:static!important;width:100%!important;height:auto!important;margin-top:12px!important;padding:14px!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:10px!important}
.parent-list div{height:auto!important;min-height:64px!important;padding:10px!important;font-size:18px!important;border:1px solid #e6e9e5!important;border-radius:8px!important}
.parent-list b{font-size:13px!important}
.parent-list small{font-size:11px!important;line-height:1.4!important}
.security{position:static!important;width:auto!important;margin:14px 0 0!important;font-size:12px!important;line-height:1.6!important}

/* story then FAQ */
.story-faq{display:block!important}
.story-card,.faq-card{position:relative!important;left:auto!important;top:auto!important;width:100%!important;height:auto!important;overflow:visible!important;padding:20px!important}
.story-card{margin-bottom:16px!important}
.story-card h2,.faq-card h2{width:auto!important;margin:0!important;font-size:22px!important;line-height:1.45!important;letter-spacing:0!important;white-space:normal!important}
.story-card p{position:static!important;width:auto!important;margin:14px 0 0!important;font-size:14px!important;line-height:1.85!important}
.story-card p br{display:none!important}
.faq-list{position:static!important;width:100%!important;height:auto!important;margin-top:14px!important}
.faq-list details{height:auto!important;min-height:52px!important}
.faq-list summary{padding:15px 38px 15px 12px!important;font-size:14px!important;line-height:1.5!important}
.faq-answer{padding:0 38px 14px 12px!important;font-size:13px!important;line-height:1.7!important}
.marketing-contact-link{font-size:13px!important}

/* primary conversion block: button only, no QR on phones */
.final-cta{width:100%!important;height:auto!important}
.marketing-mobile-free{width:100%!important;height:auto!important;padding:32px 18px!important}
.marketing-mobile-free-inner{width:100%!important;min-height:0!important;padding:24px 18px!important}
.marketing-mobile-free h2{font-size:24px!important;line-height:1.4!important}
.marketing-mobile-free .marketing-free-copy{font-size:14px!important;line-height:1.8!important}
.marketing-mobile-free .marketing-line-copy{font-size:14px!important}
.marketing-mobile-free .marketing-line-start{display:block!important}
.marketing-mobile-free .marketing-line-qr,.marketing-mobile-free .marketing-qr-help{display:none!important}
.marketing-mobile-free .marketing-line-button{display:flex!important;align-items:center!important;justify-content:center!important;width:100%!important;min-height:52px!important;padding:13px 16px!important;font-size:16px!important}
.marketing-mobile-free .marketing-free-note{font-size:12px!important;line-height:1.6!important}

/* principles/support are a vertical reading flow */
.mobile-trust-support{position:relative!important;width:100%!important;height:auto!important;padding:0 18px 34px!important;overflow:visible!important}
.mobile-principles-card,.mobile-support-card{position:relative!important;left:auto!important;top:auto!important;width:100%!important;height:auto!important;padding:20px!important}
.mobile-support-card{margin-top:16px!important}
.mobile-principles-card>span,.mobile-support-card>span{font-size:13px!important}
.mobile-principles-card h2,.mobile-support-card h2{font-size:22px!important;line-height:1.5!important}
.mobile-principles-card p,.mobile-support-card p{font-size:14px!important;line-height:1.8!important}
.mobile-principle-points{display:grid!important;grid-template-columns:1fr!important;gap:7px!important;white-space:normal!important}
.mobile-principle-points b{font-size:13px!important;text-align:center!important}
.mobile-support-amounts{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:9px!important}
.mobile-support-amounts b{height:44px!important;font-size:14px!important}
.mobile-support-cap{font-size:12px!important;line-height:1.6!important}
.mobile-support-card>a{width:100%!important;height:46px!important;font-size:14px!important}
.mobile-support-card>small{font-size:12px!important;line-height:1.6!important}

/* mobile footer */
.footer{position:relative!important;width:100%!important;height:auto!important;min-height:0!important;padding:22px 18px!important}
.footer nav{position:static!important;height:auto!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:12px 18px!important;font-size:13px!important}
.footer nav i{display:none!important}
.footer small{position:static!important;display:block!important;margin-top:20px!important;font-size:11px!important}

/* never let fixed preview descendants create page-level horizontal scrolling */
img{max-width:100%!important}
a,button,p,h1,h2,h3,h4,small,b,strong,span{overflow-wrap:anywhere}
@media(max-width:360px){
  .problem-grid,.feature-grid{grid-template-columns:1fr!important}
  .mobile-question-stats{gap:3px!important;padding-inline:10px!important}
  .mobile-question-stats b{font-size:19px!important}
  .parent-board{grid-template-columns:1fr!important}
  .parent-board>strong,.parent-progress,.parent-message{grid-column:1!important}
}
</style>"""


def _marketing_styles() -> str:
    return """<style id="marketing-refresh-v02">
.header-actions .btn.primary{margin-left:auto}
.header-actions .btn.primary{width:170px!important;white-space:nowrap!important;font-size:12px!important}
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
.free-beta-hero-notice{display:flex;flex-wrap:wrap;align-items:center;gap:7px 10px;margin:16px 0 2px!important}
.free-beta-hero-notice strong,.free-beta-hero-notice span{display:inline-flex;align-items:center;min-height:28px;padding:5px 10px;border-radius:999px;font-size:11px;line-height:1.35}
.free-beta-hero-notice strong{background:#f5f8f5;border:1px solid #d9e5db;color:#294032}
.free-beta-hero-notice span{background:#fff3c9;border:1px solid #e7c96b;color:#785b00;font-weight:700}
@media(min-width:761px){
  .hero{height:370px!important}
  .hero-inner{height:370px!important}
  .hero .free-beta-hero-notice{margin:20px 0 0!important}
  .hero .free-beta-hero-notice strong,.hero .free-beta-hero-notice span{min-height:32px!important;padding:7px 13px!important;font-size:14px!important}
  .hero .free-beta-hero-notice span{font-size:15px!important;font-weight:800!important;border-color:#d9b94e!important;box-shadow:0 2px 7px rgba(120,91,0,.08)!important}
  .hero .hero-actions{margin-top:22px!important}
  .hero .hero-actions .secondary{border-color:#d8ded9!important;background:#fff!important;color:#59645d!important;font-weight:600!important;box-shadow:none!important}
}
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
@media(max-width:760px){.page{height:2884px!important}.hero{height:430px!important}.hero-visual{height:430px!important}.hero .free-beta-hero-notice{position:absolute;z-index:3;left:62px;top:205px;width:365px;margin:0!important}.hero .free-beta-hero-notice strong,.hero .free-beta-hero-notice span{display:inline-flex;width:auto;max-width:100%;min-height:18px;margin:0 3px 3px 0;padding:2px 7px;font-size:7px}.hero .chips{top:250px!important}.hero .video-card{top:284px!important}.marketing-line-start{flex-direction:column}.marketing-qr-help{display:none}.marketing-free-copy br{display:none}.marketing-mobile-free .marketing-line-qr{display:none!important}.marketing-mobile-free-inner{min-height:250px!important}}
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
    html = html.replace("提供条件を準備中", "無料モニター 先着30名限定")
    html = html.replace("料金・提供条件は公開準備中", "無料モニター 先着30名限定")
    if mobile:
        html = _prepare_mobile_layout(html)
    html = re.sub(r'<style id="marketing-refresh-v0[12]">.*?</style>', "", html, flags=re.DOTALL)
    styles = _marketing_styles()
    if mobile:
        styles += _mobile_responsive_styles()
    html = html.replace("</head>", styles + "</head>", 1)
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
