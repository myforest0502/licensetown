"""Compatibility alias for licensetown.common.developer_status."""

import sys
from licensetown.common import developer_status as _implementation
sys.modules[__name__] = _implementation
