"""Compatibility alias for licensetown.pt.exam_weight_shadow."""

import sys
from licensetown.pt import exam_weight_shadow as _implementation
sys.modules[__name__] = _implementation
