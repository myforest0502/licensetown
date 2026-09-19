"""Compatibility alias for licensetown.pt.prerequisite_attempt_cache."""

import sys
from licensetown.pt import prerequisite_attempt_cache as _implementation
sys.modules[__name__] = _implementation
