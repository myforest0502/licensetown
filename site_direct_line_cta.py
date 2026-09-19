"""Compatibility alias for licensetown.pt.site_direct_line_cta."""

import sys
from licensetown.pt import site_direct_line_cta as _implementation
sys.modules[__name__] = _implementation
