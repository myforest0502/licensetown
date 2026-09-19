"""Compatibility alias for licensetown.pt.question_equivalence."""

import sys
from licensetown.pt import question_equivalence as _implementation
sys.modules[__name__] = _implementation
