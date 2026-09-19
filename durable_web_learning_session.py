"""Compatibility alias for licensetown.common.durable_web_learning_session."""

import sys
from licensetown.common import durable_web_learning_session as _implementation
sys.modules[__name__] = _implementation
