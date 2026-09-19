"""Compatibility alias for licensetown.common.site_marketing_viewport_fix."""

import sys
from licensetown.common import site_marketing_viewport_fix as _implementation
sys.modules[__name__] = _implementation
