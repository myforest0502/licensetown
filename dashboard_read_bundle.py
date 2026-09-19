"""Compatibility alias for licensetown.pt.dashboard_read_bundle."""

import sys
from licensetown.pt import dashboard_read_bundle as _implementation
sys.modules[__name__] = _implementation
