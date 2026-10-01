"""TODO: compatibility shim for licensetown.pt.qualification_dashboard_scope."""

import sys
from licensetown.pt import qualification_dashboard_scope as _implementation
sys.modules[__name__] = _implementation
