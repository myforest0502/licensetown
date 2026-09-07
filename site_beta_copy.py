from __future__ import annotations

from flask import request


_REPLACEMENTS = (
    (
        "現在は検証期間中のため、利用料金はいただいていません。実際に使っていただきながら改善を続けています。",
        "現在はβ期間のため、完全版の機能を無料で開放しています。実際に使っていただきながら改善を続けています。",
    ),
    (
        "ありません。将来、有料化する場合は事前にHPなどでお知らせします。知らないうちに料金が発生することはありません。",
        "ありません。正式リリース後は一部機能を月額プランにする予定ですが、料金が発生する場合は事前にHPなどでお知らせします。知らないうちに料金が発生することはありません。",
    ),
    ("検証期間中 無料公開", "β期間中 完全版を無料開放"),
    (
        "LicenseTownは現在、実際に使っていただきながら改善を続けています。<br>検証期間中は利用料金をいただいていません。",
        "LicenseTownは現在、実際に使っていただきながら改善を続けています。<br>β期間中は完全版の機能を無料で開放しています。",
    ),
    (
        "※将来、有料化する場合は事前にHPなどでお知らせします。知らないうちに料金が発生することはありません。",
        "※正式リリース後は一部機能を月額プランにする予定です。料金が発生する場合は事前にご案内し、知らないうちに課金されることはありません。",
    ),
    (
        "LicenseTownは現在、検証期間中のため無料で利用できます。",
        "LicenseTownは現在β期間中のため、完全版の機能を無料で利用できます。",
    ),
)


def install_site_beta_copy(app) -> None:
    @app.after_request
    def apply_site_beta_copy(response):
        if response.status_code != 200 or response.mimetype != "text/html" or response.direct_passthrough:
            return response
        if request.path not in {"/site/view/pc", "/site/view/mobile", "/site/line-start"}:
            return response
        html = response.get_data(as_text=True)
        for before, after in _REPLACEMENTS:
            html = html.replace(before, after)
        response.set_data(html)
        response.headers["Content-Length"] = str(len(response.get_data()))
        return response
