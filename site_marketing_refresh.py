"""Compatibility alias for licensetown.pt.site_marketing_refresh."""

import sys
from licensetown.pt import site_marketing_refresh as _implementation
sys.modules[__name__] = _implementation
