"""Compatibility alias for licensetown.pt.dashboard_real_data_shadow."""

import sys
from licensetown.pt import dashboard_real_data_shadow as _implementation
sys.modules[__name__] = _implementation
