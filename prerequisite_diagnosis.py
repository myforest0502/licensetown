"""Compatibility alias for licensetown.pt.prerequisite_diagnosis."""

import sys
from licensetown.pt import prerequisite_diagnosis as _implementation
sys.modules[__name__] = _implementation
