from pathlib import Path

path = Path("pilot_diagnostics.py")
text = path.read_text(encoding="utf-8")

marker = '''\n\ndef build_saved_adaptive_daily_audit(events):\n'''
helper = '''\n\ndef _parse_adaptive_session_event_key(event_key):\n    """Return (session_id, set_no) for the persisted ``{session_id}:{set_no}`` form."""\n    head, separator, tail = str(event_key or "").rpartition(":")\n    if not separator or not head or not tail.isdigit():\n        return None\n    set_no = int(tail)\n    if set_no < 1:\n        return None\n    return head, set_no\n\n\ndef _adaptive_session_completion_status(events, question_count, unique_question_count):\n    parsed = [_parse_adaptive_session_event_key(event.get("event_key")) for event in events]\n    parsed_set_numbers = [item[1] for item in parsed if item is not None]\n    parsed_session_ids = [item[0] for item in parsed if item is not None]\n    if len(events) != 6:\n        status = "event_count_incomplete"\n    elif any(item is None for item in parsed):\n        status = "event_key_unparseable"\n    elif len(set(parsed_session_ids)) != 1:\n        status = "mixed_session_ids"\n    elif len(set(parsed_set_numbers)) != len(parsed_set_numbers) or set(parsed_set_numbers) != set(range(1, 7)):\n        status = "set_sequence_invalid"\n    elif question_count != 30:\n        status = "question_count_incomplete"\n    elif unique_question_count != 30:\n        status = "duplicate_question_ids"\n    else:\n        status = "complete"\n    return {\n        "session_status": status,\n        "parsed_session_ids": parsed_session_ids,\n        "parsed_set_numbers": parsed_set_numbers,\n        "event_key_parse_failure_count": sum(item is None for item in parsed),\n    }\n'''
if helper not in text:
    if text.count(marker) != 1:
        raise SystemExit(f"helper marker count={text.count(marker)}")
    text = text.replace(marker, helper + marker)

old = '''    unique_question_count = len({item["question_id"] for item in details})\n    expected_question_count = 30\n    session_complete = (\n        len(events) == 6\n        and len(details) == expected_question_count\n        and unique_question_count == expected_question_count\n    )\n    return {'''
new = '''    unique_question_count = len({item["question_id"] for item in details})\n    expected_question_count = 30\n    completion = _adaptive_session_completion_status(\n        events, len(details), unique_question_count\n    )\n    session_complete = completion["session_status"] == "complete"\n    return {'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"completion target count={text.count(old)}")
    text = text.replace(old, new)

old_return = '''        "expected_question_count": expected_question_count,\n        "session_complete": session_complete,\n        "question_count": len(details),'''
new_return = '''        "expected_question_count": expected_question_count,\n        "session_complete": session_complete,\n        "session_status": completion["session_status"],\n        "parsed_session_ids": completion["parsed_session_ids"],\n        "parsed_set_numbers": completion["parsed_set_numbers"],\n        "event_key_parse_failure_count": completion["event_key_parse_failure_count"],\n        "question_count": len(details),'''
if new_return not in text:
    if text.count(old_return) != 1:
        raise SystemExit(f"return target count={text.count(old_return)}")
    text = text.replace(old_return, new_return)

path.write_text(text, encoding="utf-8")
