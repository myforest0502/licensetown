"""TODO: compatibility shim for licensetown.pt.qualification_history_scope."""

import sys
from licensetown.pt import qualification_history_scope as _implementation
sys.modules[__name__] = _implementation
