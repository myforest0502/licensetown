"""Compatibility alias for licensetown.takken.config."""

import sys
from licensetown.takken import config as _implementation
sys.modules[__name__] = _implementation
