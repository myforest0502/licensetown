"""TODO: compatibility shim for licensetown.pt.qualification_learning_writer_scope."""

import sys
from licensetown.pt import qualification_learning_writer_scope as _implementation
sys.modules[__name__] = _implementation
