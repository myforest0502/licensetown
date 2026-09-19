"""Compatibility alias for licensetown.common.site_marketing_refresh."""

import sys
from licensetown.common import site_marketing_refresh as _implementation
sys.modules[__name__] = _implementation
