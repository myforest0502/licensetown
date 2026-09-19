"""Compatibility alias for licensetown.common.durable_paused_session."""

import sys
from licensetown.common import durable_paused_session as _implementation
sys.modules[__name__] = _implementation
