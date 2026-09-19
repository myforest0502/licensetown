"""Compatibility alias for licensetown.pt.field_evidence."""

import sys
from licensetown.pt import field_evidence as _implementation
sys.modules[__name__] = _implementation
