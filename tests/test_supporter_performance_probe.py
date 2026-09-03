import logging
import os
from time import sleep

import supporter_performance as perf


def test_probe_is_disabled_by_default(monkeypatch, caplog):
    monkeypatch.delenv("LT_SUPPORTER_PERF_LOG", raising=False)
    caplog.set_level(logging.INFO)
    assert perf.begin_request() is None
    with perf.measure("disabled"):
        pass
    perf.finish_request(200)
    assert "lt_supporter_perf" not in caplog.text


def test_probe_logs_trace_operation_and_total_without_identifiers(monkeypatch, caplog):
    monkeypatch.setenv("LT_SUPPORTER_PERF_LOG", "1")
    caplog.set_level(logging.INFO)
    trace_id = perf.begin_request()
    assert trace_id
    with perf.measure("db.question_attempts"):
        sleep(0.001)
    perf.finish_request(200)
    text = caplog.text
    assert f"trace={trace_id}" in text
    assert "op=db.question_attempts" in text
    assert "op=http_total" in text
    assert "status=200" in text
    assert "duration_ms=" in text
