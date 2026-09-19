"""Compatibility alias for licensetown.pt.progress_shadow_audit."""

import sys
from licensetown.pt import progress_shadow_audit as _implementation
sys.modules[__name__] = _implementation
