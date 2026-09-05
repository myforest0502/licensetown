from term_explainer import clean_term_query, explain_term, search_term_records


def _records():
    return [
        {
            "question_id": "Q10",
            "question_text": "FIMについて正しいのはどれか。",
            "choices": ("運動項目", "認知項目"),
            "explanation": "FIMは日常生活動作の自立度を評価する尺度である。運動項目と認知項目で構成される。",
            "choice_explanations": ("FIMでは介助量を評価する。",),
            "knowledge_node": "FIM",
            "category_name": "理学療法評価各論",
        },
        {
            "question_id": "Q20",
            "question_text": "ADL評価について正しいのはどれか。",
            "choices": ("FIM", "MMT"),
            "explanation": "ADL評価には複数の尺度がある。",
            "choice_explanations": ("FIMはADL評価尺度の一つである。",),
            "knowledge_node": "ADL評価",
            "category_name": "理学療法評価各論",
        },
    ]


def test_clean_term_query_removes_conversational_wrapper():
    assert clean_term_query("源さん、FIMとは？") == "FIM"
    assert clean_term_query("相反性抑制について教えて") == "相反性抑制"


def test_search_prefers_exact_knowledge_node_and_explanation_evidence():
    results = search_term_records("FIM", _records(), limit=3)
    assert [item.question_id for item in results] == ["Q10", "Q20"]
    assert results[0].score > results[1].score
    assert any("FIM" in snippet for snippet in results[0].snippets)


def test_search_returns_no_evidence_for_unknown_term():
    assert search_term_records("未知用語", _records()) == []


def test_explain_term_short_query_requests_more_specific_input():
    message = explain_term("a")
    assert "もう少し具体的" in message


def test_explain_term_does_not_claim_definition_without_bank_evidence(monkeypatch):
    monkeypatch.setattr("term_explainer.search_term_records", lambda _term: [])
    message = explain_term("未知用語")
    assert "意味を断定できるだけの記述を見つけられなかった" in message
    assert "推測" not in message or "推測では" not in message
