"""Compatibility alias for licensetown.common.learner_navigation_performance."""

import sys
from licensetown.common import learner_navigation_performance as _implementation
sys.modules[__name__] = _implementation
