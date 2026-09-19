"""Compatibility alias for licensetown.pt.daily_wrong_review."""

import sys
from licensetown.pt import daily_wrong_review as _implementation
sys.modules[__name__] = _implementation
