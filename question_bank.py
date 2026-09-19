"""Compatibility alias for licensetown.pt.question_bank."""

import sys
from licensetown.pt import question_bank as _implementation
sys.modules[__name__] = _implementation
