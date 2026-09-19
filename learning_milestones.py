"""Compatibility alias for licensetown.pt.learning_milestones."""

import sys
from licensetown.pt import learning_milestones as _implementation
sys.modules[__name__] = _implementation
