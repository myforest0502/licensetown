"""Compatibility alias for licensetown.pt.field_progress."""

import sys
from licensetown.pt import field_progress as _implementation
sys.modules[__name__] = _implementation
