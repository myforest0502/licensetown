"""Compatibility alias for licensetown.common.qualification_dashboard_scope."""

import sys
from licensetown.common import qualification_dashboard_scope as _implementation
sys.modules[__name__] = _implementation
