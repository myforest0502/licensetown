"""Compatibility alias for licensetown.pt.config."""

import sys
from licensetown.pt import config as _implementation
sys.modules[__name__] = _implementation
