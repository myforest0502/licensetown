"""Compatibility alias for licensetown.pt.goukaku_ui."""

import sys
from licensetown.pt import goukaku_ui as _implementation
sys.modules[__name__] = _implementation
