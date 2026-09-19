"""Compatibility alias for licensetown.pt.supporter_report."""

import sys
from licensetown.pt import supporter_report as _implementation
sys.modules[__name__] = _implementation
