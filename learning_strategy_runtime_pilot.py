"""Compatibility alias for licensetown.pt.learning_strategy_runtime_pilot."""

import sys
from licensetown.pt import learning_strategy_runtime_pilot as _implementation
sys.modules[__name__] = _implementation
