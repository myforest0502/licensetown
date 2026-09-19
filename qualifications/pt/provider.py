"""Compatibility alias for licensetown.pt.provider."""

import sys
from licensetown.pt import provider as _implementation
sys.modules[__name__] = _implementation
