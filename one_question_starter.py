"""Compatibility alias for licensetown.pt.one_question_starter."""

import sys
from licensetown.pt import one_question_starter as _implementation
sys.modules[__name__] = _implementation
