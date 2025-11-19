"""Utility helpers for benchmarks."""

from __future__ import annotations

import statistics
from typing import Iterable, Sequence


def percentile(values: Sequence[float] | Iterable[float], pct: float) -> float:
    """Compute percentile without external deps; falls back to mean when empty."""
    vals = list(values)
    if not vals:
        return 0.0
    vals.sort()
    k = (len(vals) - 1) * (pct / 100)
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    if f == c:
        return vals[int(k)]
    d0 = vals[f] * (c - k)
    d1 = vals[c] * (k - f)
    return d0 + d1


def mean(values: Sequence[float] | Iterable[float]) -> float:
    """Safe mean with zero fallback."""
    vals = list(values)
    return statistics.mean(vals) if vals else 0.0
