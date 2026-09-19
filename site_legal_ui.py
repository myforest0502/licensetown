"""Compatibility alias for licensetown.common.site_legal_ui."""

import sys
from licensetown.common import site_legal_ui as _implementation
sys.modules[__name__] = _implementation
