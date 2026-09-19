"""Compatibility alias for licensetown.pt.prerequisite_backtrack_pilot."""

import sys
from licensetown.pt import prerequisite_backtrack_pilot as _implementation
sys.modules[__name__] = _implementation
