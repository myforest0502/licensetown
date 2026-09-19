"""Compatibility alias for licensetown.common.site_ui."""

import sys
from licensetown.common import site_ui as _implementation
sys.modules[__name__] = _implementation
