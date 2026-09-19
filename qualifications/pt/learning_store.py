"""Compatibility alias for licensetown.pt.learning_store."""

import sys
from licensetown.pt import learning_store as _implementation
sys.modules[__name__] = _implementation
