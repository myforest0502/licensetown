"""Compatibility alias for licensetown.common.learning_store_registry."""

import sys
from licensetown.common import learning_store_registry as _implementation
sys.modules[__name__] = _implementation
