from pathlib import Path

path = Path("templates/goukaku/supporter_pilot_diagnostics.html")
text = path.read_text(encoding="utf-8")
old = '''    <p>source {{ saved.source }} / mode {{ saved.mode }} / event数 {{ saved.event_count }}</p>\n    {% if saved.session_complete %}<p><b>30問監査完了</b></p>{% else %}<p><b>進行中: {{ saved.question_count }}/{{ saved.expected_question_count }}問</b></p>{% endif %}\n    <p>問題数 {{ saved.question_count }} / unique Q {{ saved.unique_question_count }}</p>'''
new = '''    <p>source {{ saved.source }} / mode {{ saved.mode }} / event数 {{ saved.event_count }}</p>\n    <p><b>session status:</b> {{ saved.session_status or '不明' }} / set番号 {{ saved.parsed_set_numbers|join(', ') if saved.parsed_set_numbers else '解析不可' }}{% if saved.event_key_parse_failure_count %} / key parse failure {{ saved.event_key_parse_failure_count }}{% endif %}</p>\n    {% if saved.session_complete %}<p><b>30問監査完了</b></p>{% else %}<p><b>未完了: {{ saved.question_count }}/{{ saved.expected_question_count }}問</b></p>{% endif %}\n    <p>問題数 {{ saved.question_count }} / unique Q {{ saved.unique_question_count }}</p>'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"template target count={text.count(old)}")
    text = text.replace(old, new)
path.write_text(text, encoding="utf-8")
