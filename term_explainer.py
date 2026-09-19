"""Compatibility alias for licensetown.pt.term_explainer."""

import sys
from licensetown.pt import term_explainer as _implementation
sys.modules[__name__] = _implementation
