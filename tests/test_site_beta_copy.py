from flask import Flask

from site_beta_copy import install_site_beta_copy


def test_public_hp_beta_copy_is_explicit():
    app = Flask(__name__)
    app.add_url_rule(
        "/site/view/pc",
        "pc",
        lambda: (
            "<html><body>"
            "検証期間中 無料公開"
            "LicenseTownは現在、実際に使っていただきながら改善を続けています。<br>"
            "検証期間中は利用料金をいただいていません。"
            "※将来、有料化する場合は事前にHPなどでお知らせします。"
            "知らないうちに料金が発生することはありません。"
            "</body></html>"
        ),
    )
    install_site_beta_copy(app)

    html = app.test_client().get("/site/view/pc").get_data(as_text=True)
    assert "β期間中 完全版を無料開放" in html
    assert "β期間中は完全版の機能を無料で開放しています" in html
    assert "正式リリース後は一部機能を月額プランにする予定です" in html
    assert "知らないうちに課金されることはありません" in html
