"""Compatibility alias for licensetown.pt.short_term_repeat_guard."""

import sys
from licensetown.pt import short_term_repeat_guard as _implementation
sys.modules[__name__] = _implementation
