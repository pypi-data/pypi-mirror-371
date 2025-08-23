"""Naming helpers for duckdantic traits."""

from __future__ import annotations

from collections.abc import Iterable
from hashlib import sha1
from typing import Any, get_args, get_origin


def short_type_token(t: Any) -> str:
    """Return a concise, human-readable token for a type expression.

    Examples:
        >>> short_type_token(str)
        'str'
        >>> short_type_token(list[str])
        'list[str]'
    """
    o = get_origin(t)
    if o is None:
        return getattr(t, "__name__", str(t))
    args = ",".join(short_type_token(a) for a in get_args(t))
    name = getattr(o, "__name__", str(o).split(".")[-1])
    return f"{name}[{args}]" if args else name


def auto_name(prefix: str, pairs: Iterable[tuple[str, Any]], maxlen: int = 80) -> str:
    """Generate a deterministic trait name from field pairs.

    Args:
        prefix: Prefix such as 'Trait' or a domain category.
        pairs: Iterable of (field_name, type_expr) pairs.
        maxlen: Maximum length of the returned name.

    Returns:
        A stable string like 'Trait_query_lang__a1b2c3d4'.
    """
    pairs = list(pairs)
    preview = "_".join([n for n, _ in pairs[:3]]) or "fields"
    sig = ",".join(f"{n}:{short_type_token(t)}" for n, t in pairs)
    digest = sha1(sig.encode("utf-8")).hexdigest()[:8]
    name = f"{prefix}_{preview}__{digest}"
    return name[:maxlen]
