"""Offline-only audit regression; fixtures never represent Production people."""
import copy
import importlib.util
import json
import socket
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from scripts import audit_learning_strategy_shadow as audit


def sample(count=65):
    from question_bank import get_question_tag
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    return [{'id': n+1, 'event_number': n//5+1, 'question_id': f'Q{n+1}',
             'knowledge_node_id': get_question_tag(f'Q{n+1}')['knowledge_node_id'],
             'answered_at': (start+timedelta(minutes=n//5)).isoformat(),
             'attempt_position': n%5+1, 'selected_answers': ['1'],
             'confidence': 1, 'is_correct': True,
             'user_id': 'PRIVATE-LEARNER', 'email': 'PRIVATE-EMAIL',
             'selection_group': 'PRIVATE-METADATA'} for n in range(count)]


def test_no_database_network_or_input_runtime_mutation(monkeypatch):
    import psycopg
    import field_evidence
    original = field_evidence.build_field_evidence
    before_db = sys.modules.get('database')
    def forbidden(*a, **k):
        pytest.fail('audit attempted DB/network access')
    monkeypatch.setattr(psycopg, 'connect', forbidden)
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    source = sample()
    saved = copy.deepcopy(source)
    result = audit.replay(source)
    assert source == saved
    assert sys.modules.get('database') is before_db
    assert field_evidence.build_field_evidence is original
    assert result['shadow_only'] and not result['selection_authority']
    text = json.dumps(result)
    assert 'PRIVATE-' not in text
    assert 'user_id' not in text and 'event_key' not in text
    assert result['production_connection'] == 'NOT YET'
    assert all('additional_blocks_completed' in c['missing_context'] for c in result['checkpoints'])


def test_private_loader_preserves_formal_evidence():
    from field_evidence import build_field_evidence
    rows = audit.normalize(sample())
    assert audit._evidence_builder()(rows, as_of=rows[-1]['answered_at']) == build_field_evidence(rows, as_of=rows[-1]['answered_at'])
    with pytest.raises(RuntimeError, match='forbidden'):
        audit._deny_database()


def test_timestamp_ties_not_split():
    records = sample(65)
    for r in records[25:35]:
        r['answered_at'] = records[25]['answered_at']
    rows = audit.normalize(records)
    assert audit.checkpoint_positions(rows) == [35,60,65]


def test_no_future_leakage():
    source = sample(95)
    before = audit.replay(source)
    source[70]['is_correct'] = False
    source[70]['confidence'] = 3
    after = audit.replay(source)
    assert before['checkpoints'][0] == after['checkpoints'][0]
    assert before['checkpoints'][1] == after['checkpoints'][1]


def test_repeat_equivalence_supply_never_relaxes():
    from question_bank import get_question_tag, get_category_small
    row = sample(1)[0]
    row.update(question_id='Q972',knowledge_node_id=get_question_tag('Q972')['knowledge_node_id'])
    rows = audit.normalize([row])
    supply = audit.eligible_supply(rows,get_category_small('Q972'),rows[0]['answered_at'])
    assert supply['after_exact_and_formal_state'] < supply['static_raw_supply']
    assert supply['eligible_supply'] <= supply['after_exact_and_formal_state']
    assert not supply['cooldown_relaxed']
    small = audit.eligible_supply(rows,14,rows[0]['answered_at'])
    assert small['eligible_supply_insufficient']


def test_small_supply_labels_remain_cautious():
    from question_bank import question_ids, get_category_small, get_question_tag
    q = next(q for q in question_ids() if get_category_small(q)==14)
    source = sample(65)
    for r in source:
        r.update(question_id=q, knowledge_node_id=get_question_tag(q)['knowledge_node_id'])
    result = audit.replay(source)
    field = result['final_fields'][13]
    assert field['field_state'] == 'assessing'
    assert 'small_supply_limitation' in field['evaluation_status']


def test_reject_empty_duplicate_and_unknown_questions():
    with pytest.raises(ValueError):
        audit.normalize([])
    rows = sample(2)
    rows[1]['id'] = rows[0]['id']
    with pytest.raises(ValueError):
        audit.normalize(rows)
    rows = sample(1)
    rows[0]['question_id'] = 'NOT-A-QUESTION'
    with pytest.raises(ValueError,match='Unknown bank question'):
        audit.replay(rows)


def test_import_has_no_runtime_imports():
    # Inspect its AST imports: runtime modules are loaded only inside replay
    # helpers; importing the CLI cannot initialize database/app/field evidence.
    import ast
    tree = ast.parse(Path(audit.__file__).read_text(encoding='utf-8'))
    imports = [n.module for n in tree.body if isinstance(n,ast.ImportFrom)]
    assert not set(imports) & {'database','app','field_evidence','learning_strategy_shadow'}
