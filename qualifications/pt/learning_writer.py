"""Compatibility alias for licensetown.pt.learning_writer."""

import sys
from licensetown.pt import learning_writer as _implementation
sys.modules[__name__] = _implementation
