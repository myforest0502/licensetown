"""Compatibility alias for licensetown.pt.field_evaluation_shadow."""

import sys
from licensetown.pt import field_evaluation_shadow as _implementation
sys.modules[__name__] = _implementation
