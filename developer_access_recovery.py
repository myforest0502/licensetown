"""Compatibility alias for licensetown.common.developer_access_recovery."""

import sys
from licensetown.common import developer_access_recovery as _implementation
sys.modules[__name__] = _implementation
