from __future__ import annotations

import math


def bounded_exponential_backoff(
    initial_seconds: float,
    maximum_seconds: float,
    failure_count: int,
) -> float:
    """Return a deterministic exponential delay capped by the configured maximum."""

    if initial_seconds <= 0:
        raise ValueError("initial_seconds must be positive")
    if maximum_seconds <= 0:
        raise ValueError("maximum_seconds must be positive")
    if failure_count < 1:
        raise ValueError("failure_count must be at least 1")
    if initial_seconds >= maximum_seconds:
        return maximum_seconds
    saturation_exponent = math.ceil(math.log2(maximum_seconds / initial_seconds))
    exponent = min(failure_count - 1, saturation_exponent)
    return min(maximum_seconds, initial_seconds * (2.0**exponent))
