from datetime import datetime,timezone,timedelta
import ast
from pathlib import Path
import pytest

import learning_strategy_runtime_pilot as pilot
import adaptive_question_selector as selector
from question_bank import question_ids,get_category_small,get_quiz_question,get_question_tag

NOW=datetime(2026,9,15,tzinfo=timezone.utc)


def test_gate_requires_both_flag_and_exact_user():
    assert not pilot.pilot_enabled(False,'a',{'a'})
    assert not pilot.pilot_enabled(True,'b',{'a'})
    assert not pilot.pilot_enabled(True,'',set())
    assert pilot.pilot_enabled(True,'a',{'a'})


def test_app_off_and_nonpilot_preserve_selector_call_without_event_read(monkeypatch):
    # Exercise the real function source with the established isolated harness
    # style: avoid unrelated Flask/LINE effects and enforce lazy imports.
    source=Path('app.py').read_text(encoding='utf-8')
    tree=ast.parse(source)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='start_quiz')
    calls=[]
    qs=[get_quiz_question(q) for q in list(question_ids())[:30]]
    ns={'QUIZ_QUESTION_COUNT':30,'QUESTIONS_PER_SET':5,'quiz_category_selections':{},
        'get_question_attempts':lambda u:[], 'ENABLE_NODE_ADAPTIVE_RECOMMENDATION':True,
        'NODE_ADAPTIVE_RECOMMENDATION_PILOT_USER_IDS':{'a'},
        'is_node_adaptive_recommendation_enabled':lambda *a:True,
        'build_node_adaptive_session':lambda *a,**k:calls.append((a,k)) or qs,
        'study_sessions':{},'user_modes':{},'format_quiz_messages':lambda qs:qs,
        'time':__import__('time'),'logging':__import__('logging'),'ENABLE_LEARNING_STRATEGY_V1':False,
        'LEARNING_STRATEGY_PILOT_USER_IDS':{'a'}}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'app.py','exec'),ns)
    import database
    monkeypatch.setattr(database,'get_learning_events',lambda *a:pytest.fail('unexpected new read'))
    for enabled,user in ((False,'a'),(True,'b')):
        ns['ENABLE_LEARNING_STRATEGY_V1']=enabled
        ns['start_quiz'](user,session_kind='adaptive_daily')
    assert len(calls)==2
    assert all(call[0]==([],30) and set(call[1])=={'exclude_ids','audit_out'} for call in calls)
    observed=[]
    monkeypatch.setattr(database,'get_learning_events',lambda u:observed.append(u) or [])
    def broken(*a,**k):
        raise ValueError('unavailable')
    monkeypatch.setattr(pilot,'refine_session',broken)
    ns['start_quiz']('a',session_kind='adaptive_daily')
    assert observed==['a']
    assert {q['id'] for q in ns['study_sessions']['a']['all_questions']}=={q['id'] for q in qs}


def setup_refinement(monkeypatch,field=18):
    baseline=[get_quiz_question(q) for q in list(question_ids())[:30]]
    audit={q['id']:{'selection_group':'repair','selection_reason':'previous_wrong_unconfirmed'} for q in baseline}
    for q in baseline[:3]: audit[q['id']]['selection_group']='exploration'
    audit[baseline[3]['id']]['selection_reason']='safety_wrong'
    audit[baseline[4]['id']]['selection_reason']='recheck_due'
    strategy={'recommended_field_id':field,'learning_intent':'coverage','priority_score':0.7,
              'reason_codes':['high_exam_weight'],'priority_components':{'coverage_gap_score':1}}
    monkeypatch.setattr(pilot,'strategy_snapshot',lambda *a:strategy)
    return baseline,audit


def test_field_handoff_preserves_safety_due_and_342_slots(monkeypatch):
    baseline,audit=setup_refinement(monkeypatch)
    spy=[]
    real=selector.select_node_adaptive_questions
    def selected(*args,**kwargs):
        spy.append(kwargs)
        return real(*args,**kwargs)
    monkeypatch.setattr(selector,'select_node_adaptive_questions',selected)
    result=pilot.refine_session([],baseline,audit,[],as_of=NOW)
    assert len(result)==30
    assert spy[0]['category_small']==18 and spy[0]['learning_intent']=='exploration'
    assert {q['id'] for q in baseline[:5]} <= {q['id'] for q in result}
    assert all(a['strategy_recommended_field']==18 for a in audit.values())
    assert all(a['strategy_shadow_or_authority']=='soft_pilot' for a in audit.values())
    assert sum(get_category_small(q['id'])==18 for q in result)>0


def test_small_supply_falls_back_without_selector_relaxation(monkeypatch):
    baseline,audit=setup_refinement(monkeypatch,14)
    monkeypatch.setattr(selector,'select_node_adaptive_questions',lambda *a,**k:pytest.fail('supply fallback missing'))
    assert pilot.refine_session([],baseline,audit,[],as_of=NOW) is baseline
    assert all(a['strategy_fallback_reason']=='eligible_supply_insufficient' for a in audit.values())


def test_72h_exact_and_recent_exclusions_reach_selector(monkeypatch):
    baseline,audit=setup_refinement(monkeypatch)
    q='Q972'
    attempts=[{'user_id':'a','question_id':q,'knowledge_node_id':get_question_tag(q)['knowledge_node_id'],
               'is_correct':False,'confidence':1,'answered_at':NOW-timedelta(hours=1),
               'event_key':'e','attempt_position':1}]
    real=selector.select_node_adaptive_questions
    def selected(*a,**k):
        from question_equivalence import canonicalize_question_evidence_id as eq
        assert eq('Q1354') in k['exclude_ids']
        return real(*a,**k)
    monkeypatch.setattr(selector,'select_node_adaptive_questions',selected)
    result=pilot.refine_session(attempts,baseline,audit,[],as_of=NOW)
    assert not {'Q972','Q1354'} & {q['id'] for q in result}


def test_completion_context_rejects_goals_as_evidence_and_future():
    events=[{'answered_at':NOW-timedelta(days=1),'mode':'recommendation_plan',
             'question_results':{'field':'生理学','goal':999}}]
    assert pilot.completion_context(events,NOW)[2]['consecutive_field_blocks']==0
    with pytest.raises(ValueError,match='unavailable'):
        pilot.completion_context(events,NOW-timedelta(days=2))


def test_partial_pilot_session_does_not_fake_completed_block():
    events=[{'answered_at':NOW-timedelta(hours=1),'event_key':'session:1','mode':'study',
             'question_results':[{'strategy_version':pilot.VERSION,
                 'strategy_shadow_or_authority':'soft_pilot','strategy_recommended_field':2,'question_id':'Q1'}]}]
    with pytest.raises(ValueError,match='Incomplete'):
        pilot.completion_context(events,NOW)


def test_completed_web_sessions_restore_observed_blocks():
    events=[]
    for i in range(3):
        at=NOW-timedelta(days=4-i)
        events.append({'answered_at':at,'mode':'recommendation_plan',
                       'question_results':{'field':'生理学','goal':999}})
        for n in range(1,11):
            events.append({'answered_at':at+timedelta(minutes=n),'mode':'study',
                           'event_key':f'web-recommendation:s{i}:{n}',
                           'question_results':[{'question_id':f'Q{n}'}]})
    context=pilot.completion_context(events,NOW)
    assert context[2]['consecutive_field_blocks']==1
    assert context[1]['consecutive_field_blocks']==0


def test_mixed_pilot_completion_credits_actual_field_questions_only():
    target=[q for q in question_ids() if get_category_small(q)==18][:20]
    others=[q for q in question_ids() if get_category_small(q)!=18][:10]
    events=[]
    for session_index in range(2):
        events.append({'answered_at':NOW-timedelta(hours=3-session_index),
            'mode':'study','event_key':f'pilot{session_index}:6',
            'question_results':[{'question_id':q,'strategy_version':pilot.VERSION,
                'strategy_shadow_or_authority':'soft_pilot','strategy_recommended_field':18}
                for q in target+others]})
    assert pilot.completion_context(events[:1],NOW)[18]['consecutive_field_blocks']==0
    assert pilot.completion_context(events,NOW)[18]['consecutive_field_blocks']==1


def test_strategy_metadata_reaches_existing_batch_payload():
    tree=ast.parse(Path('app.py').read_text(encoding='utf-8'))
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='record_confirmed_learning_batch')
    captured=[]
    ns={'get_question_tag':get_question_tag,'is_answer_correct':lambda *a:True,
        'selected_answers_for_history':lambda q,a:a,
        'record_learning_batch':lambda **kw:captured.append(kw)}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'app.py','exec'),ns)
    meta={k:'test-value' for k in pilot.METADATA_KEYS}
    session={'current_set':1,'questions_per_set':1,'session_id':'test',
             'questions':[get_quiz_question('Q1')], 'all_answers':{1:{'answer':['1'],'confidence':1}},
             'session_kind':'adaptive_daily','adaptive_selection_audit':{'Q1':meta}}
    ns['record_confirmed_learning_batch']('anonymous',session)
    assert all(captured[0]['question_results'][0][k]==v for k,v in meta.items())


def test_real_strategy_snapshot_has_no_direct_q_authority():
    from tests.test_learning_strategy_natural_history_audit import sample
    from scripts.audit_learning_strategy_shadow import normalize
    attempts=normalize(sample())
    events=[{'answered_at':NOW-timedelta(days=1),'mode':'recommendation_plan',
             'question_results':{'field':'生理学','goal':10}}]
    result=pilot.strategy_snapshot(attempts,events,NOW)
    assert result['shadow_only'] and not result['selection_authority']
    assert result['recommended_field_id'] in range(1,19)
    assert all('additional_blocks_completed' not in r['target']['context_available'] for r in result['ranked_fields'])
