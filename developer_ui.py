"""Compatibility alias for licensetown.pt.developer_ui."""

import sys
from licensetown.pt import developer_ui as _implementation
sys.modules[__name__] = _implementation
