"""Compatibility alias for licensetown.common.question_order_quality."""

import sys
from licensetown.common import question_order_quality as _implementation
sys.modules[__name__] = _implementation
