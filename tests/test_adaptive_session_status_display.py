from pathlib import Path


def test_supporter_template_exposes_saved_session_status_and_parsed_sets():
    source = (Path(__file__).parents[1] / "templates/goukaku/supporter_pilot_diagnostics.html").read_text(encoding="utf-8")
    assert "saved.session_status" in source
    assert "saved.parsed_set_numbers" in source
    assert "saved.event_key_parse_failure_count" in source
    assert "未完了:" in source
