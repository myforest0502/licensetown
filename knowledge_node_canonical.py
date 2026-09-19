"""Compatibility alias for licensetown.pt.knowledge_node_canonical."""

import sys
from licensetown.pt import knowledge_node_canonical as _implementation
sys.modules[__name__] = _implementation
