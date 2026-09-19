"""Compatibility alias for licensetown.pt.written_understanding_check."""

import sys
from licensetown.pt import written_understanding_check as _implementation
sys.modules[__name__] = _implementation
