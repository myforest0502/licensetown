"""Compatibility alias for licensetown.common.stripe_webhook_ui."""

import sys
from licensetown.common import stripe_webhook_ui as _implementation
sys.modules[__name__] = _implementation
