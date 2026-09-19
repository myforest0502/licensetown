"""Compatibility alias for licensetown.pt.learning_strategy_shadow."""

import sys
from licensetown.pt import learning_strategy_shadow as _implementation
sys.modules[__name__] = _implementation
