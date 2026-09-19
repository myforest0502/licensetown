"""Compatibility alias for licensetown.pt.site_marketing_hotfix."""

import sys
from licensetown.pt import site_marketing_hotfix as _implementation
sys.modules[__name__] = _implementation
