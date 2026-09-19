"""Compatibility alias for licensetown.common.developer_ui."""

import sys
from licensetown.common import developer_ui as _implementation
sys.modules[__name__] = _implementation
