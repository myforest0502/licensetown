"""Compatibility alias for licensetown.pt.pilot_diagnostics."""

import sys
from licensetown.pt import pilot_diagnostics as _implementation
sys.modules[__name__] = _implementation
