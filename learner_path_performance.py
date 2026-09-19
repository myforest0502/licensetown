"""Compatibility alias for licensetown.common.learner_path_performance."""

import sys
from licensetown.common import learner_path_performance as _implementation
sys.modules[__name__] = _implementation
