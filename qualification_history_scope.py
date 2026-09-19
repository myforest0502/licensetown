"""Compatibility alias for licensetown.common.qualification_history_scope."""

import sys
from licensetown.common import qualification_history_scope as _implementation
sys.modules[__name__] = _implementation
