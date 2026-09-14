from copy import deepcopy
import json
import socket

import pytest
from scripts.audit_recommendation_plan_shadow import replay_plans
from tests.test_learning_strategy_natural_history_audit import sample


def fixture():
    return {'attempts':sample(65), 'plans':[
        {'answered_at':'2026-09-01T00:05:00+00:00','field':'生理学','goal':10},
        {'answered_at':'2026-09-01T00:10:00+00:00','field':'生理学','goal':10}],
        'sessions':[{'started_at':'2026-09-01T00:06:00+00:00',
                     'completed_at':'2026-09-01T00:08:00+00:00',
                     'answer_events':10,'answered_count':10,'min_position':1,'max_position':10}]}


def test_prefix_privacy_no_network_no_mutation(monkeypatch):
    def denied(*args,**kwargs):
        pytest.fail('network attempted')
    monkeypatch.setattr(socket.socket,'connect',denied)
    data=fixture()
    data['plans'][0].update(user_id='PRIVATE',reason_code='PRIVATE',learning_intent='PRIVATE')
    saved=deepcopy(data)
    result=replay_plans(data)
    assert result['plans'][0]['attempt_prefix_count']==25
    assert result['plans'][1]['attempt_prefix_count']==50
    assert 'PRIVATE' not in json.dumps(result)
    assert 'user_id' not in json.dumps(result)
    assert data==saved
    assert not result['selection_authority']


def test_current_completion_never_enters_preplan_context():
    data=fixture()
    before=replay_plans(data)
    data['sessions']=[]
    after=replay_plans(data)
    for key in ('consecutive_field_blocks_at_plan_time','shadow_top3_fields','shadow_priority_score'):
        assert before['plans'][0][key]==after['plans'][0][key]
    assert before['plans'][0]['completed_recommendation_questions_after_plan']==10
    assert after['plans'][0]['completed_recommendation_questions_after_plan']==0


def test_duplicate_sessions_rejected_and_partial_not_completed():
    data=fixture()
    data['sessions'].append(deepcopy(data['sessions'][0]))
    with pytest.raises(ValueError,match='Duplicate'):
        replay_plans(data)
    data=fixture()
    data['sessions'][0]['answer_events']=9
    assert replay_plans(data)['plans'][0]['completed_recommendation_questions_after_plan']==0
