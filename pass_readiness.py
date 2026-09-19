"""Compatibility alias for licensetown.pt.pass_readiness."""

import sys
from licensetown.pt import pass_readiness as _implementation
sys.modules[__name__] = _implementation
