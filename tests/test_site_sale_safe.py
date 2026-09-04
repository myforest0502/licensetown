from site_ui import _sale_safe_html


def test_pc_demo_claims_are_sanitized():
    html = "新規問題</small><b>1000<em>問</em></b> 過去問</small><b>1000<em>問</em></b> 合計</small><b>2000<em>問収録</em></b> 無料期間実施中！ すべての機能を無料で体験できます。 合格まで あと <b>123</b>日 総合達成度"
    safe = _sale_safe_html(html)
    assert "2000<em>問収録</em>" not in safe
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
