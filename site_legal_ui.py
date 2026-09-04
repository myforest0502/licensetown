"""Public legal/trust pages for the official LicenseTown site.

These pages are intentionally sale-safe while required operator fields are
missing. They provide stable public destinations now without pretending that
public charging is ready before final operator/legal review.
"""

from __future__ import annotations

import os
from html import escape

from flask import Blueprint, render_template_string


site_legal_ui = Blueprint("site_legal_ui", __name__)

_REQUIRED_OPERATOR_ENV = {
    "販売事業者": "SITE_SELLER_NAME",
    "所在地": "SITE_SELLER_ADDRESS",
    "電話番号": "SITE_SELLER_PHONE",
    "お問い合わせ先": "SITE_SUPPORT_EMAIL",
}

_OPERATOR_BRAND_ENV = "SITE_OPERATOR_BRAND"


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


def _layout(title: str, body_html: str):
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
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;background:#f7faf7;color:#18331f}
main{max-width:820px;margin:40px auto;padding:0 20px 60px}.card{background:#fff;border:1px solid #dce8de;border-radius:18px;padding:28px}
a{color:#087d2c}.notice{padding:14px 16px;background:#eef8ef;border-radius:12px;margin-bottom:24px}h1{font-size:28px}h2{margin-top:28px;font-size:20px}dt{font-weight:700;margin-top:14px}dd{margin:4px 0 0}footer{margin-top:32px;font-size:13px;color:#66756a}.support-note{padding:16px;background:#f3f8f3;border-radius:12px}.muted{color:#66756a}
</style></head><body><main><div class="card"><div class="notice">{{ status }}</div>
<h1>{{ title }}</h1>{{ body|safe }}<footer><a href="/site">LicenseTown公式サイトへ戻る</a></footer>
</div></main></body></html>
        """,
        title=title,
        status=status,
        body=body_html,
    )


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
<h2>利用目的</h2>
<p>本人確認、学習機能・弱点分析・見守り機能の提供、サポート、不正利用防止、サービス改善、契約状態の管理のために利用します。</p>
<h2>決済情報</h2>
<p>カード番号等の決済カード情報をLicenseTownのデータベースへ保存しない設計です。決済事業者が必要な決済処理を行います。</p>
<h2>見守り機能</h2>
<p>見守り相手には学習状況を共有します。個別の相談内容そのものを見守り画面へ共有しない方針です。</p>
<h2>最終確認</h2>
<p>本ページは販売開始前に、保存期間・第三者提供・委託先・開示等請求・問い合わせ窓口を含めて最終確認します。</p>
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
<p>支援する・しないは完全に任意です。支援の有無で、現在提供している学習機能に差をつける予定はありません。</p>
</div>
<h2>いただいた支援について</h2>
<p>LicenseTownの運営、レスポンス改善、AI利用、機能改善、将来のアプリ化など、サービスを良くするために活用します。</p>
<p class="muted">現在は支援受付の準備中です。決済機能はまだ公開していません。</p>
"""
    return _layout("LicenseTownを応援する", body)


@site_legal_ui.get("/site/legal/contact")
def contact():
    email = _env("SITE_SUPPORT_EMAIL")
    if email:
        body = f'<p>お問い合わせ：<a href="mailto:{escape(email)}">{escape(email)}</a></p>'
    else:
        body = "<p>お問い合わせ窓口は販売開始前に掲載します。</p>"
    return _layout("お問い合わせ", body)
