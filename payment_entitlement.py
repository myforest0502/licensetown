"""Compatibility alias for licensetown.common.payment_entitlement."""

import sys
from licensetown.common import payment_entitlement as _implementation
sys.modules[__name__] = _implementation
