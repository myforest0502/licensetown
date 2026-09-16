import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app


def test_public_site_exposes_bilingual_brand_context_and_internal_links():
    html = app.test_client().get("/site").get_data(as_text=True)

    assert "ライセンスタウン（LicenseTown）について" in html
    assert "ライセンスタウン（LicenseTown）は、理学療法士国家試験" in html
    assert 'href="/site/faq"' in html
    assert 'href="/site/legal/contact"' in html
