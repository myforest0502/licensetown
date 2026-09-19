"""Compatibility alias for licensetown.pt.prerequisite_backtrack."""

import sys
from licensetown.pt import prerequisite_backtrack as _implementation
sys.modules[__name__] = _implementation
