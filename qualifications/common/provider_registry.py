"""Compatibility alias for licensetown.common.provider_registry."""

import sys
from licensetown.common import provider_registry as _implementation
sys.modules[__name__] = _implementation
