"""Compatibility alias for licensetown.pt.overall_progress_presentation."""

import sys
from licensetown.pt import overall_progress_presentation as _implementation
sys.modules[__name__] = _implementation
