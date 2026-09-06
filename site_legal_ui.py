"""Public legal/trust pages for the official LicenseTown site.

These pages are intentionally sale-safe while required operator fields are
missing. They provide stable public destinations now without pretending that
public charging is ready before final operator/legal review.
"""

from __future__ import annotations

import os
from html import escape

from flask import Blueprint, render_template_string, request

from feedback_store import (
    FeedbackStoreUnavailable,
    FeedbackValidationError,
    VALID_CATEGORIES,
    create_feedback,
    get_feedback_for_public_status,
)


site_legal_ui = Blueprint("site_legal_ui", __name__)

_REQUIRED_OPERATOR_ENV = {
    "販売事業者": "SITE_SELLER_NAME",
    "所在地": "SITE_SELLER_ADDRESS",
    "電話番号": "SITE_SELLER_PHONE",
    "お問い合わせ先": "SITE_SUPPORT_EMAIL",
}

_OPERATOR_BRAND_ENV = "SITE_OPERATOR_BRAND"

_STATUS_LABELS = {
    "received": "受付済み",
    "reviewing": "確認中",
    "planned": "対応予定",
    "responded": "返信済み",
    "closed": "対応完了",
}


def _env(name: str) -> str:
    return str(os.getenv(name) or "").strip()


def operator_details() -> dict[str, str]:
    return {label: _env(env_name) for label, env_name in _REQUIRED_OPERATOR_ENV.items()}


def operator_brand() -> str:
    return _env(_OPERATOR_BRAND_ENV)


def _operator_rows(*, include_brand: bool = True) -> str:
    rows: list[tuple[str, str]] = []
    if include_brand and operator_brand():
        rows.append(("運営ブランド", operator_brand()))
    rows.extend(operator_details().items())
    return "".join(
        f"<dt>{escape(label)}</dt><dd>{escape(value) if value else '販売開始前に掲載'}</dd>"
        for label, value in rows
    )


def sale_legal_ready() -> bool:
    # Brand is a public-facing operating name, not a required legal identity field.
    return all(operator_details().values())


def _layout(title: str, body_html: str, *, show_sale_notice: bool = True):
    ready = sale_legal_ready()
    status = (
        "販売に必要な事業者情報を設定済みです。公開前に最終確認が必要です。"
        if ready
        else "販売開始前の準備ページです。事業者情報の確定前は公開販売の根拠として使用しません。"
    )
    return render_template_string(
        """
<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }} | LicenseTown</title>
<style>
html,body{width:100%;height:100%;margin:0;overflow:hidden}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f7faf7;color:#18331f}
main{position:fixed;inset:0;box-sizing:border-box;padding:16px 20px;display:flex;align-items:center;justify-content:center}
.card{width:min(820px,100%);max-height:calc(100dvh - 32px);box-sizing:border-box;overflow-y:auto;overscroll-behavior:contain;scrollbar-gutter:stable;background:#fff;border:1px solid #dce8de;border-radius:18px;padding:28px}
a{color:#087d2c}.notice{padding:14px 16px;background:#eef8ef;border-radius:12px;margin-bottom:24px}h1{font-size:28px}h2{margin-top:28px;font-size:20px}dt{font-weight:700;margin-top:14px}dd{margin:4px 0 0}footer{margin-top:32px;font-size:13px;color:#66756a}.support-note{padding:16px;background:#f3f8f3;border-radius:12px}.muted{color:#66756a}.support-amounts{display:flex;gap:10px;flex-wrap:wrap;padding:0;list-style:none}.support-amounts li{padding:8px 12px;border:1px solid #cfe0d2;border-radius:999px;background:#fff;font-weight:700}
.contact-lead{line-height:1.75;margin:0 0 22px}.field{margin-top:18px}.field label{display:block;font-weight:700;margin-bottom:7px}.field .hint{display:block;font-weight:400;color:#66756a;font-size:13px;margin-top:3px}.field input,.field select,.field textarea{width:100%;box-sizing:border-box;border:1px solid #c8d8cb;border-radius:10px;background:#fff;color:#18331f;font:inherit;padding:12px 13px}.field textarea{min-height:160px;resize:vertical}.field input:focus,.field select:focus,.field textarea:focus{outline:2px solid #bfe3c7;outline-offset:1px;border-color:#4aa963}.button{display:inline-block;margin-top:22px;border:0;border-radius:999px;padding:12px 22px;background:#11843a;color:#fff;font:inherit;font-weight:700;cursor:pointer}.button:hover{filter:brightness(.96)}.error{padding:12px 14px;background:#fff4f2;border:1px solid #f0c8c0;border-radius:10px;color:#84251d;margin-bottom:18px}.success{padding:14px 16px;background:#eef8ef;border-radius:12px;margin:16px 0}.receipt{font-size:20px;font-weight:800;letter-spacing:.02em}.status-box{padding:16px;background:#f3f8f3;border-radius:12px;margin:16px 0}.status-label{display:inline-block;padding:5px 10px;border-radius:999px;background:#e2f2e5;font-weight:700}.reply-box{white-space:pre-wrap;padding:14px 16px;background:#f7faf7;border:1px solid #dce8de;border-radius:10px;line-height:1.7}.privacy-note{font-size:13px;color:#66756a;line-height:1.6;margin-top:16px}.hp-field{position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden}
@media(max-width:640px){main{padding:8px}.card{max-height:calc(100dvh - 16px);padding:20px;border-radius:14px}h1{font-size:24px}.button{width:100%}}
</style>
<script>
(function(){
  function resetCard(){
    var card=document.querySelector('.card');
    if(card) card.scrollTop=0;
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',resetCard); else resetCard();
  window.addEventListener('pageshow',resetCard);
  window.addEventListener('load',resetCard);
})();
</script></head><body><main><div class="card">{% if show_sale_notice %}<div class="notice">{{ status }}</div>{% endif %}
<h1>{{ title }}</h1>{{ body|safe }}<footer><a href="/site">LicenseTown公式サイトへ戻る</a></footer>
</div></main></body></html>
        """,
        title=title,
        status=status,
        body=body_html,
        show_sale_notice=show_sale_notice,
    )


def _contact_form(*, values: dict[str, str] | None = None, error: str = "") -> str:
    values = values or {}
    category = values.get("category", "")
    options = ['<option value="">選択してください</option>']
    for value, label in VALID_CATEGORIES.items():
        selected = " selected" if category == value else ""
        options.append(f'<option value="{escape(value)}"{selected}>{escape(label)}</option>')
    error_html = f'<div class="error" role="alert">{escape(error)}</div>' if error else ""
    return f"""
<p class="contact-lead">不具合や使いにくいところ、「こうしてほしい」というご要望、使い方についての質問などをお送りください。小さなことでも大歓迎です。</p>
{error_html}
<form method="post" action="/site/legal/contact#top" novalidate>
  <div class="field">
    <label for="name">お名前 <span class="hint">ニックネームでも可・任意</span></label>
    <input id="name" name="name" type="text" maxlength="80" autocomplete="name" value="{escape(values.get('name', ''))}">
  </div>
  <div class="field">
    <label for="email">返信先メールアドレス <span class="hint">任意</span></label>
    <input id="email" name="email" type="email" maxlength="254" autocomplete="email" value="{escape(values.get('email', ''))}">
    <span class="hint">未入力でも送信できます。メール返信機能は現在準備中のため、当面は送信後に表示される確認ページをご利用ください。</span>
  </div>
  <div class="field">
    <label for="category">お問い合わせ種類</label>
    <select id="category" name="category" required>{''.join(options)}</select>
  </div>
  <div class="field">
    <label for="message">お問い合わせ内容</label>
    <textarea id="message" name="message" maxlength="4000" required>{escape(values.get('message', ''))}</textarea>
  </div>
  <div class="hp-field" aria-hidden="true">
    <label for="website">Web site</label><input id="website" name="website" type="text" tabindex="-1" autocomplete="off">
  </div>
  <p class="privacy-note">送信内容は、お問い合わせへの対応とLicenseTownの改善のために利用します。返信先メールアドレスを入力した場合は、返信のためにも利用します。</p>
  <button class="button" type="submit">送信する</button>
</form>
"""


@site_legal_ui.get("/site/legal/commercial-transactions")
def commercial_transactions():
    rows = _operator_rows()
    body = f"""
<p>特定商取引法に基づく表記の公開先です。販売開始前に必要事項を確定します。</p>
<dl>{rows}
<dt>サービス名</dt><dd>LicenseTown</dd>
<dt>販売価格</dt><dd>申込画面で税込価格を表示します。現在は販売準備中です。</dd>
<dt>支払方法</dt><dd>販売開始時に申込画面で案内します。</dd>
<dt>提供時期</dt><dd>決済完了後、利用権限の反映を確認して提供します。</dd>
<dt>解約</dt><dd>月額契約を採用する場合、解約後も契約期間終了までは利用可能とする設計です。最終条件は販売開始前に明示します。</dd>
</dl>
"""
    return _layout("特定商取引法に基づく表記", body)


@site_legal_ui.get("/site/legal/privacy")
def privacy():
    body = """
<p>LicenseTownは、学習サービスの提供に必要な範囲で利用者情報を取り扱います。</p>
<h2>取り扱う主な情報</h2>
<p>LINE等のアカウント識別情報、学習履歴、回答結果、学習進捗、サービス利用状況、契約・利用権限に関する情報など。</p>
<h2>お問い合わせ情報</h2>
<p>お問い合わせフォームから送信された内容、入力されたお名前またはニックネーム、返信先メールアドレス（任意）を、お問い合わせ対応とサービス改善のために取り扱います。返信先メールアドレスは、入力された場合に返信のためにも利用します。</p>
<h2>利用目的</h2>
<p>本人確認、学習機能・弱点分析・見守り機能の提供、サポート、不正利用防止、サービス改善、契約状態の管理のために利用します。</p>
<h2>決済情報</h2>
<p>カード番号等の決済カード情報をLicenseTownのデータベースへ保存しない設計です。決済事業者が必要な決済処理を行います。</p>
<h2>見守り機能</h2>
<p>見守り相手には学習状況を共有します。個別の相談内容そのものを見守り画面へ共有しない方針です。</p>
<h2>最終確認</h2>
<p>本ページは販売開始前に、保存期間・第三者提供・委託先・開示等請求を含めて最終確認します。</p>
"""
    return _layout("プライバシーポリシー", body)


@site_legal_ui.get("/site/legal/terms")
def terms():
    body = """
<p>本規約はLicenseTownの利用条件を定めるための公開先です。</p>
<h2>サービスの位置づけ</h2>
<p>LicenseTownは理学療法士国家試験等の学習を支援するサービスです。合格を保証するものではありません。</p>
<h2>アカウント</h2>
<p>利用者は自己のアカウントを適切に管理し、第三者による不正利用を防ぐものとします。</p>
<h2>学習データ</h2>
<p>契約状態が変化しても、学習履歴を直ちに削除しない設計です。退会・削除の最終条件は販売開始前に明示します。</p>
<h2>禁止事項・免責・変更</h2>
<p>不正アクセス、サービス妨害、権利侵害等を禁止します。詳細な免責、規約変更、準拠法・管轄等は販売開始前の最終レビューで確定します。</p>
"""
    return _layout("利用規約", body)


@site_legal_ui.get("/site/legal/operator")
def operator():
    rows = _operator_rows()
    return _layout("運営者情報", f"<dl>{rows}<dt>サービス名</dt><dd>LicenseTown</dd></dl>")


@site_legal_ui.get("/site/support")
def support():
    body = """
<p><strong>LicenseTownは現在、より多くの方に使っていただき、改善を重ねることを優先しています。</strong></p>
<p>使いにくいところ、わかりにくいところ、もっとこうしてほしいという声を集めながら、少しずつ良いサービスに育てていきます。</p>
<h2>もっと良くしたいこと</h2>
<p>レスポンスをもっと速くすること。スマートフォンでもっと使いやすくすること。将来はアプリとして使えるようにすること。問題・分析・学習提案をさらに磨くこと。</p>
<p>そのためには、サーバー代、AI利用料、開発や運営のための費用がかかります。</p>
<div class="support-note">
<strong>もし「これからも続いてほしい」「少し応援してもいい」と思っていただけたら、無理のない範囲で開発支援をいただけると嬉しいです。</strong>
<p>支援する・しないは完全に任意です。支援の有無で、現在提供している学習機能に差はつけません。</p>
<p>当面の支援額は100円・300円・500円・1,000円の4つだけにし、1回あたり1,000円を上限とします。それ以上の金額は受け付けません。</p>
<ul class="support-amounts"><li>100円</li><li>300円</li><li>500円</li><li>1,000円</li></ul>
</div>
<h2>いただいた支援について</h2>
<p>LicenseTownの運営、レスポンス改善、AI利用、機能改善、将来のアプリ化など、サービスを良くするために活用します。</p>
<h2>大切にすること</h2>
<p><strong>LicenseTownは、これからも「誠実」であることを大切にします。</strong></p>
<p>まだ胸を張って完成したと言える段階ではないからこそ、今は利用者の声を集め、改善を続けることを優先します。支援はサービス利用の条件ではなく、応援したいと思ってくださる方からのお気持ちとして受け取ります。</p>
<p class="muted">現在は支援受付の準備中です。決済機能はまだ公開していません。</p>
"""
    return _layout("LicenseTownを応援する", body)


@site_legal_ui.route("/site/legal/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return _layout("お問い合わせ", _contact_form(), show_sale_notice=False)

    values = {
        "name": str(request.form.get("name") or ""),
        "email": str(request.form.get("email") or ""),
        "category": str(request.form.get("category") or ""),
        "message": str(request.form.get("message") or ""),
    }

    # Quietly absorb simple bot submissions without writing them to the inbox.
    if str(request.form.get("website") or "").strip():
        body = """
<div class="success"><strong>お問い合わせを受け付けました。</strong></div>
<p>ご連絡ありがとうございました。</p>
"""
        return _layout("お問い合わせ", body, show_sale_notice=False)

    try:
        receipt = create_feedback(
            name=values["name"],
            email=values["email"],
            category=values["category"],
            message=values["message"],
            source="web",
            page_path=request.path,
        )
    except FeedbackValidationError as exc:
        return _layout(
            "お問い合わせ",
            _contact_form(values=values, error=str(exc)),
            show_sale_notice=False,
        ), 400
    except FeedbackStoreUnavailable:
        return _layout(
            "お問い合わせ",
            _contact_form(
                values=values,
                error="現在お問い合わせを保存できません。時間をおいて、もう一度お試しください。",
            ),
            show_sale_notice=False,
        ), 503
    except Exception:
        return _layout(
            "お問い合わせ",
            _contact_form(
                values=values,
                error="送信中に問題が発生しました。時間をおいて、もう一度お試しください。",
            ),
            show_sale_notice=False,
        ), 503

    token = escape(receipt.tracking_token, quote=True)
    public_id = escape(receipt.public_id)
    body = f"""
<div class="success"><strong>お問い合わせを受け付けました。</strong></div>
<p>受付番号</p><p class="receipt">{public_id}</p>
<p>こちらで内容を確認します。お問い合わせ状況と運営からの返信は、下の専用ページから確認できます。</p>
<p><a class="button" href="/site/legal/contact/status?token={token}#top">お問い合わせ状況を確認する</a></p>
<p class="privacy-note">この確認ページのURLは、他の人に共有しないでください。受付番号だけでは内容を表示できません。</p>
"""
    return _layout("お問い合わせ", body, show_sale_notice=False), 201


@site_legal_ui.get("/site/legal/contact/status")
def contact_status():
    token = str(request.args.get("token") or "").strip()
    if not token:
        body = """
<p>お問い合わせ送信後に表示された専用の確認URLから開いてください。</p>
<p><a href="/site/legal/contact#top">お問い合わせフォームへ</a></p>
"""
        return _layout("お問い合わせ状況", body, show_sale_notice=False), 400

    try:
        item = get_feedback_for_public_status(token)
    except FeedbackStoreUnavailable:
        item = None

    if not item:
        body = """
<p>このお問い合わせを確認できませんでした。URLが途中で切れていないか確認してください。</p>
<p><a href="/site/legal/contact#top">お問い合わせフォームへ</a></p>
"""
        return _layout("お問い合わせ状況", body, show_sale_notice=False), 404

    status_label = _STATUS_LABELS.get(str(item.get("status") or ""), "確認中")
    category_label = VALID_CATEGORIES.get(str(item.get("category") or ""), "その他")
    reply = str(item.get("operator_reply") or "").strip()
    reply_html = (
        f'<h2>運営からの返信</h2><div class="reply-box">{escape(reply)}</div>'
        if reply
        else '<p class="muted">運営からの返信はまだありません。</p>'
    )
    body = f"""
<div class="status-box">
<p><strong>受付番号：</strong>{escape(str(item['public_id']))}</p>
<p><strong>種類：</strong>{escape(category_label)}</p>
<p><strong>状況：</strong> <span class="status-label">{escape(status_label)}</span></p>
</div>
{reply_html}
<p class="privacy-note">このページには、お名前・メールアドレス・送信本文は表示しません。</p>
"""
    return _layout("お問い合わせ状況", body, show_sale_notice=False)
