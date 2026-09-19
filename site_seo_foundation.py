"""Compatibility alias for licensetown.common.site_seo_foundation."""

import sys
from licensetown.common import site_seo_foundation as _implementation
sys.modules[__name__] = _implementation
