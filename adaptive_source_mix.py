"""Compatibility alias for licensetown.pt.adaptive_source_mix."""

import sys
from licensetown.pt import adaptive_source_mix as _implementation
sys.modules[__name__] = _implementation
