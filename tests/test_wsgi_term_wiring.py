import wsgi


def test_gensan_explain_uses_local_term_explainer(monkeypatch):
    monkeypatch.setattr(wsgi, "explain_term", lambda text: f"LOCAL:{text}")

    assert wsgi.create_text_response("FIM", mode="gensan_explain") == "LOCAL:FIM"


def test_home_advertises_term_tool_instead_of_consultation():
    message = wsgi.create_home_message()
    items = message.quick_reply.items
    labels = [item.action.label for item in items]
    texts = [getattr(item.action, "text", None) for item in items]

    assert "❓ 教えて源さん" in labels
    assert "教えて源さん" in texts
    assert "💬 相談する" not in labels
    assert "相談する" not in texts


def test_legacy_module_is_wired_for_registered_handlers():
    assert wsgi.legacy.create_text_response is wsgi.create_text_response
    assert wsgi.legacy.create_home_message is wsgi.create_home_message
