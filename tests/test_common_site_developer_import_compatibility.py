"""Shared site/developer modules keep legacy import identity."""

import importlib

MODULES = ["developer_access_recovery","developer_ui","site_beta_copy","site_direct_line_cta","site_legal_ui","site_marketing_hotfix","site_marketing_refresh","site_marketing_viewport_fix","site_seo_foundation"]

def test_shared_site_and_developer_imports_are_canonical():
    for name in MODULES:
        legacy = importlib.import_module(name)
        canonical = importlib.import_module(f"licensetown.common.{name}")
        assert legacy is canonical
