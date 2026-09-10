from datetime import datetime, timezone

import learning_engine as engine
import short_term_repeat_guard as guard
from question_equivalence import canonicalize_question_evidence_id


NOW = datetime(2026, 9, 10, 12, tzinfo=timezone.utc)


class FirstChoiceRandom:
    def shuffle(self, values):
        return None

    def choice(self, values):
        return values[0]


def test_initial_assessment_never_contains_two_raw_ids_for_same_exact_evidence(monkeypatch):
    candidates = ["Q1411", "Q1585"] + [f"Q{i}" for i in range(1, 21)]
    monkeypatch.setattr(engine, "_candidate_ids", lambda *_args, **_kwargs: list(candidates))
    monkeypatch.setattr(
        engine,
        "get_question_tag",
        lambda q_id: {"primary_ability": "KNOW", "level": (int(q_id[1:]) % 4) + 1},
    )
    monkeypatch.setattr(engine, "get_quiz_question", lambda q_id: {"id": q_id})

    selected = engine.build_initial_assessment(10, rng=FirstChoiceRandom())
    selected_ids = [item["id"] for item in selected]
    evidence_ids = [canonicalize_question_evidence_id(q_id) for q_id in selected_ids]

    assert len(selected_ids) == 10
    assert len(evidence_ids) == len(set(evidence_ids))
    assert len({"Q1411", "Q1585"} & set(selected_ids)) == 1


def test_unknown_attempt_time_fails_closed_for_three_day_floor():
    attempts = [{
        "user_id": "learner",
        "question_id": "Q1",
        "knowledge_node_id": "KN0001",
        "is_correct": True,
        "confidence": 1,
        "answer_status": "answered",
    }]

    assert guard.recent_short_term_evidence_ids(attempts, as_of=NOW) == {"Q1"}
