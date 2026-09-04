from site_ui import (
    PREVIEW_724_DIR,
    PREVIEW_PC_DIR,
    _public_onboarding_url,
    _question_count_label,
    _sale_safe_html,
    _sale_safe_source,
)


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


def test_question_count_defaults_to_formal_bank(monkeypatch):
    monkeypatch.delenv("SITE_QUESTION_COUNT_LABEL", raising=False)
    assert _question_count_label() == "1737問収録"


def test_mobile_copy_typo_free_claim_and_count_are_sanitized(monkeypatch):
    monkeypatch.delenv("SITE_QUESTION_COUNT_LABEL", raising=False)
    html = "<li>現在無料</li><li>LINEで使える</li><li>1,500問以上収録</li> 金融内容（個別のやり取り）は共有されません。"
    safe = _sale_safe_html(html)
    assert "現在無料" not in safe
    assert "金融内容" not in safe
    assert "相談内容（個別のやり取り）は共有されません。" in safe
    assert "1,500問以上収録" not in safe
    assert "1737問収録" in safe


def test_public_cta_fails_closed_until_verified_https_url(monkeypatch):
    monkeypatch.delenv("SITE_ONBOARDING_URL", raising=False)
    assert _public_onboarding_url() == "/site/legal/contact"
    safe = _sale_safe_html('<a class="btn primary">まずは使ってみる　›</a>')
    assert 'href="/site/legal/contact"' in safe

    monkeypatch.setenv("SITE_ONBOARDING_URL", "javascript:alert(1)")
    assert _public_onboarding_url() == "/site/legal/contact"

    monkeypatch.setenv("SITE_ONBOARDING_URL", "https://example.test/line-entry")
    assert _public_onboarding_url() == "https://example.test/line-entry"
    safe = _sale_safe_html('<a class="header-cta" href="#try">まずは使ってみる</a>')
    assert 'href="https://example.test/line-entry"' in safe


def test_pc_source_asset_no_longer_contains_stale_2000_or_free_period():
    html = (PREVIEW_PC_DIR / "index.html").read_text(encoding="utf-8")
    assert "2000" not in html
    assert "無料期間実施中" not in html
    assert "1737" in html


def test_public_mobile_source_response_is_sale_safe(monkeypatch):
    monkeypatch.delenv("SITE_QUESTION_COUNT_LABEL", raising=False)
    response = _sale_safe_source(PREVIEW_724_DIR / "index.html")
    html = response.get_data(as_text=True)
    assert "現在無料" not in html
    assert "金融内容" not in html
    assert "相談内容（個別のやり取り）は共有されません。" in html
    assert "1737問収録" in html
