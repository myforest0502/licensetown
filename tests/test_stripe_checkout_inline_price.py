import stripe_checkout_service as service


def test_inline_monthly_price_is_sandbox_configurable(monkeypatch):
    monkeypatch.delenv("STRIPE_SANDBOX_PRICE_ID", raising=False)
    monkeypatch.setenv("STRIPE_SANDBOX_MONTHLY_AMOUNT_JPY", "100")

    item = service._checkout_line_item()

    assert item == {
        "price_data": {
            "currency": "jpy",
            "unit_amount": 100,
            "recurring": {"interval": "month"},
            "product_data": {"name": "LicenseTown sandbox monthly"},
        },
        "quantity": 1,
    }


def test_inline_monthly_price_rejects_non_positive_amount(monkeypatch):
    monkeypatch.delenv("STRIPE_SANDBOX_PRICE_ID", raising=False)
    monkeypatch.setenv("STRIPE_SANDBOX_MONTHLY_AMOUNT_JPY", "0")
    try:
        service._checkout_line_item()
    except RuntimeError as exc:
        assert "STRIPE_SANDBOX" in str(exc)
    else:
        raise AssertionError("non-positive sandbox price must be rejected")
