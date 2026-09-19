"""Compatibility alias for licensetown.common.supporter_performance."""

import sys
from licensetown.common import supporter_performance as _implementation
sys.modules[__name__] = _implementation
