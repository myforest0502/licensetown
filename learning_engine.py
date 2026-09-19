"""Compatibility alias for licensetown.pt.learning_engine."""

import sys
from licensetown.pt import learning_engine as _implementation
sys.modules[__name__] = _implementation
