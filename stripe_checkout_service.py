"""Compatibility alias for licensetown.common.stripe_checkout_service."""

import sys
from licensetown.common import stripe_checkout_service as _implementation
sys.modules[__name__] = _implementation
