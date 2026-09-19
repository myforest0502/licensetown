"""Compatibility alias for licensetown.common.email_delivery."""

import sys
from licensetown.common import email_delivery as _implementation
sys.modules[__name__] = _implementation
