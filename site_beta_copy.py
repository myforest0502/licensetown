"""Compatibility alias for licensetown.pt.site_beta_copy."""

import sys
from licensetown.pt import site_beta_copy as _implementation
sys.modules[__name__] = _implementation
