"""Compatibility alias for licensetown.pt.knowledge_node_relations."""

import sys
from licensetown.pt import knowledge_node_relations as _implementation
sys.modules[__name__] = _implementation
