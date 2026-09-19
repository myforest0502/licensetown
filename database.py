"""Compatibility alias for licensetown.common.database."""

import sys
from licensetown.common import database as _implementation
sys.modules[__name__] = _implementation
