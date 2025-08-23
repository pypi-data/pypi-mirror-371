"""Memoization helpers for normalization."""

from __future__ import annotations

from typing import Any

from duckdantic.fields import FieldView
from duckdantic.normalize import normalize_fields
from duckdantic.shapes import shape_id_token

_CACHE: dict[str, dict[str, FieldView]] = {}
_HITS = 0
_MISSES = 0


def normalize_fields_cached(obj: Any) -> dict[str, FieldView]:
    """Normalize fields with a small in-process cache keyed by shape ID.

    The cache is keyed by :func:`shapes.shape_id_token`. Because
    normalization does not depend on policy, this provides a stable and
    safe memoization layer across repeated checks.
    """
    global _HITS, _MISSES
    key = shape_id_token(obj)
    try:
        v = _CACHE[key]
    except KeyError:
        v = normalize_fields(obj)
        _CACHE[key] = v
        _MISSES += 1
    else:
        _HITS += 1
    return v


def get_cache_stats() -> dict:
    """Return simple cache statistics."""
    return {"size": len(_CACHE), "hits": _HITS, "misses": _MISSES}


def clear_cache() -> None:
    """Clear the normalization cache and reset stats."""
    global _HITS, _MISSES
    _CACHE.clear()
    _HITS = 0
    _MISSES = 0
