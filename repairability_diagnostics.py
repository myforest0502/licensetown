"""Compatibility alias for licensetown.pt.repairability_diagnostics."""

import sys
from licensetown.pt import repairability_diagnostics as _implementation
sys.modules[__name__] = _implementation
