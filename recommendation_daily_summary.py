"""Compatibility alias for licensetown.common.recommendation_daily_summary."""

import sys
from licensetown.common import recommendation_daily_summary as _implementation
sys.modules[__name__] = _implementation
