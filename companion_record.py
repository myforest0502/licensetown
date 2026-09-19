"""Compatibility alias for licensetown.pt.companion_record."""

import sys
from licensetown.pt import companion_record as _implementation
sys.modules[__name__] = _implementation
