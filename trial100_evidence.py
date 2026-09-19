"""Compatibility alias for licensetown.pt.trial100_evidence."""

import sys
from licensetown.pt import trial100_evidence as _implementation
sys.modules[__name__] = _implementation
