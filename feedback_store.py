"""Compatibility alias for licensetown.common.feedback_store."""

import sys
from licensetown.common import feedback_store as _implementation
sys.modules[__name__] = _implementation
