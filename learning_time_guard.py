"""Compatibility alias for licensetown.common.learning_time_guard."""

import sys
from licensetown.common import learning_time_guard as _implementation
sys.modules[__name__] = _implementation
