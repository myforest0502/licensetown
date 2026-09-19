"""Compatibility alias for licensetown.pt.developer_access_recovery."""

import sys
from licensetown.pt import developer_access_recovery as _implementation
sys.modules[__name__] = _implementation
