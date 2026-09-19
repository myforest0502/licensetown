"""Compatibility alias for licensetown.pt.adaptive_question_selector."""

import sys
from licensetown.pt import adaptive_question_selector as _implementation
sys.modules[__name__] = _implementation
