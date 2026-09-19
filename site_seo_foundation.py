"""Compatibility alias for licensetown.pt.site_seo_foundation."""

import sys
from licensetown.pt import site_seo_foundation as _implementation
sys.modules[__name__] = _implementation
