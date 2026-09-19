"""Compatibility alias for licensetown.pt.dashboard_settings."""

import sys
from licensetown.pt import dashboard_settings as _implementation
sys.modules[__name__] = _implementation
