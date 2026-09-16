from goukaku_ui import SUPPORTER_TOKEN_MAX_AGE_SECONDS


def test_supporter_token_lifetime_is_long_lived():
    """Parent monitoring links must not silently expire after one month."""
    assert SUPPORTER_TOKEN_MAX_AGE_SECONDS >= 365 * 24 * 60 * 60
