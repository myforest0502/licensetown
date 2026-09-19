"""Compatibility alias for licensetown.pt.phase11_session_load_facts."""

import sys
from licensetown.pt import phase11_session_load_facts as _implementation
sys.modules[__name__] = _implementation
