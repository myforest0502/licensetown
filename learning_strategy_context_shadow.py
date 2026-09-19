"""Compatibility alias for licensetown.pt.learning_strategy_context_shadow."""

import sys
from licensetown.pt import learning_strategy_context_shadow as _implementation
sys.modules[__name__] = _implementation
