"""Compatibility alias for licensetown.common.payment_access."""

import sys
from licensetown.common import payment_access as _implementation
sys.modules[__name__] = _implementation
