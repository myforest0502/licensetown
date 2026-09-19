"""Compatibility alias for licensetown.common.site_direct_line_cta."""

import sys
from licensetown.common import site_direct_line_cta as _implementation
sys.modules[__name__] = _implementation
