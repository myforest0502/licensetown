"""Compatibility alias for licensetown.pt.judgment_shadow."""

import sys
from licensetown.pt import judgment_shadow as _implementation
sys.modules[__name__] = _implementation
