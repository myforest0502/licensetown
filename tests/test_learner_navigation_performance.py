import logging

import learner_navigation_performance as performance


def test_timing_is_off_by_default(monkeypatch, caplog):
    monkeypatch.delenv("LT_LEARNER_NAVIGATION_PERF_LOG", raising=False)
    with caplog.at_level(logging.INFO):
        timing = performance.RequestTiming()
        with timing.measure("formal_input_read"):
            pass
        timing.finish(200)
    assert "lt_learner_navigation_perf" not in caplog.text


def test_timing_logs_only_stage_duration_and_status(monkeypatch, caplog):
    monkeypatch.setenv("LT_LEARNER_NAVIGATION_PERF_LOG", "true")
    with caplog.at_level(logging.INFO):
        timing = performance.RequestTiming()
        with timing.measure("formal_input_read"):
            pass
        timing.finish(200)
    assert "op=formal_input_read" in caplog.text
    assert "op=route_total" in caplog.text
    assert "status=200" in caplog.text
    assert "user_id" not in caplog.text
    assert "token" not in caplog.text
