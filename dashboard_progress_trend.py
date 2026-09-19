"""Compatibility alias for licensetown.pt.dashboard_progress_trend."""

import sys
from licensetown.pt import dashboard_progress_trend as _implementation
sys.modules[__name__] = _implementation
