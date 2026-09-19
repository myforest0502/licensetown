"""Compatibility alias for licensetown.common.stripe_billing_ui."""

import sys
from licensetown.common import stripe_billing_ui as _implementation
sys.modules[__name__] = _implementation
