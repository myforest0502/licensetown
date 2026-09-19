"""Compatibility entry for licensetown.pt.field_evidence.

Normal imports resolve to the canonical PT module. Offline audit tools also load
this file directly under a private module name, so expose the canonical symbols
in that temporary module without changing its loader identity.
"""

import sys
from licensetown.pt import field_evidence as _implementation

for _name, _value in vars(_implementation).items():
    if _name not in {"__name__", "__package__", "__loader__", "__spec__"}:
        globals()[_name] = _value

if __name__ == "field_evidence":
    sys.modules[__name__] = _implementation
