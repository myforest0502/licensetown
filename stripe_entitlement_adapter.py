"""Compatibility alias for licensetown.common.stripe_entitlement_adapter."""

import sys
from licensetown.common import stripe_entitlement_adapter as _implementation
sys.modules[__name__] = _implementation
