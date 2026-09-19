"""Compatibility alias for licensetown.pt.trial100_store."""

import sys
from licensetown.pt import trial100_store as _implementation
sys.modules[__name__] = _implementation
