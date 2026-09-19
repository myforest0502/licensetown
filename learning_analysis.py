"""Compatibility alias for licensetown.pt.learning_analysis."""

import sys
from licensetown.pt import learning_analysis as _implementation
sys.modules[__name__] = _implementation
