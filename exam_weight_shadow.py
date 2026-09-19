"""Compatibility alias for the PT-specific exam-weight model.

Both import paths resolve to one module, preserving function globals and patches.
The implementation lives in qualifications.pt; no policy or data changes here.
"""
import sys

from qualifications.pt import exam_weight_shadow as _implementation

sys.modules[__name__] = _implementation
