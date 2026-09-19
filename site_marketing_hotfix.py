"""Compatibility alias for licensetown.common.site_marketing_hotfix."""

import sys
from licensetown.common import site_marketing_hotfix as _implementation
sys.modules[__name__] = _implementation
