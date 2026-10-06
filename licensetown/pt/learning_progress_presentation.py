"""Pure learner progress calculation; never an input to learning decisions."""

import math


def normalize_progress_ratio(value, *, scale=1):
    """Clamp finite numeric inputs; missing or invalid evidence contributes zero."""
    try:
        ratio = float(value) / scale
    except (TypeError, ValueError, OverflowError):
        return 0.0
    return max(0.0, min(1.0, ratio)) if math.isfinite(ratio) else 0.0


def calculate_learning_progress(coverage, accuracy, finish):
    """Combine scope, scope-weighted accuracy and unchanged Node maturity."""
    coverage = normalize_progress_ratio(coverage)
    accuracy = normalize_progress_ratio(accuracy)
    finish = normalize_progress_ratio(finish)
    return normalize_progress_ratio(0.30 * coverage + 0.40 * coverage * accuracy + 0.30 * finish)
