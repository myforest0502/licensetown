from site_ui import PREVIEW_724_DIR, PREVIEW_PC_DIR, _sale_safe_html, _sale_safe_source


def test_pc_demo_claims_are_sanitized():
    html = (
        '<section class="stats"><div class="container"><div><i>▰</i><span><small>新規問題</small>'
        '<b>1000<em>問</em></b></span></div><div><i>▤</i><span><small>過去問</small>'
        '<b>1000<em>問</em></b></span></div><div><i>▥</i><span><small>合計</small>'
        '<b>2000<em>問収録</em></b></span></div></div></section>'
        ' 無料期間実施中！ すべての機能を無料で体験できます。 '
        '合格まで あと <b>123</b>日 総合達成度</small>'
    )
    safe = _sale_safe_html(html)
    assert "2000<em>問収録</em>" not in safe
    assert "1000<em>問</em>" not in safe
    assert "無料期間実施中！" not in safe
    assert "すべての機能を無料で体験できます。" not in safe
    assert "画面イメージ" in safe


def test_mobile_copy_typo_and_free_claim_are_sanitized():
    html = "<li>現在無料</li><li>LINEで使える</li><li>1,500問以上収録</li> 金融内容（個別のやり取り）は共有されません。"
    safe = _sale_safe_html(html)
    assert "現在無料" not in safe
    assert "金融内容" not in safe
    assert "相談内容（個別のやり取り）は共有されません。" in safe
    assert "1,500問以上収録" in safe


def test_pc_source_asset_no_longer_contains_stale_2000_or_free_period():
    html = (PREVIEW_PC_DIR / "index.html").read_text(encoding="utf-8")
    assert "2000" not in html
    assert "無料期間実施中" not in html
    assert "1737" in html


def test_public_mobile_source_response_is_sale_safe():
    response = _sale_safe_source(PREVIEW_724_DIR / "index.html")
    html = response.get_data(as_text=True)
    assert "現在無料" not in html
    assert "金融内容" not in html
    assert "相談内容（個別のやり取り）は共有されません。" in html
