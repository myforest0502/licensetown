"""Compatibility alias for licensetown.common.site_beta_copy."""

import sys
from licensetown.common import site_beta_copy as _implementation
sys.modules[__name__] = _implementation
