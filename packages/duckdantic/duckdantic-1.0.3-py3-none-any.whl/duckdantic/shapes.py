"""Shape identification utilities and stable ID tokens.

This module provides a lightweight way to assign a stable *identity
token* to classes, instances, and mappings that can be normalized into
fields. The token is designed to be deterministic across processes for
the same structural inputs, and is suitable for memoization keys.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from hashlib import sha1
from typing import Any, Protocol, get_type_hints

from duckdantic.naming import short_type_token


class ShapeOrigin(Enum):
    """Provenance of the input object."""

    CLASS = "class"
    INSTANCE = "instance"
    MAPPING = "mapping"


class ModelShape(Protocol):
    """Abstract representation of a shape that can be normalized."""

    origin: ShapeOrigin

    def id_token(self) -> str: ...
    def source(self) -> Any: ...  # returns underlying source object


@dataclass(frozen=True)
class ClassShape:
    cls: type
    origin: ShapeOrigin = ShapeOrigin.CLASS

    def id_token(self) -> str:
        mod = getattr(self.cls, "__module__", "<unknown>")
        qn = getattr(
            self.cls,
            "__qualname__",
            getattr(
                self.cls,
                "__name__",
                "<anon>",
            ),
        )
        # include a signature of annotations so changes bust the cache
        hints = get_type_hints(self.cls, include_extras=True)
        sig = ",".join(f"{k}:{short_type_token(v)}" for k, v in sorted(hints.items()))
        digest = sha1(sig.encode("utf-8")).hexdigest()[:10]
        return f"cls:{mod}.{qn}:{digest}"

    def source(self) -> Any:
        return self.cls


@dataclass(frozen=True)
class InstanceShape:
    obj: Any
    origin: ShapeOrigin = ShapeOrigin.INSTANCE

    def id_token(self) -> str:
        # Instances normalize through their class; don't include id(obj)
        cls = self.obj.__class__
        return ClassShape(cls).id_token()

    def source(self) -> Any:
        return self.obj


@dataclass(frozen=True)
class MappingShape:
    mapping: Mapping[str, Any]
    origin: ShapeOrigin = ShapeOrigin.MAPPING

    def id_token(self) -> str:
        # For stable IDs independent of dict order, sort by key and derive a type token
        parts = []
        for k, v in sorted(self.mapping.items(), key=lambda kv: kv[0]):
            ann = getattr(v, "annotation", None)
            if ann is not None:
                t = ann
            else:
                # FieldView case: has .annotation; if absent, treat as type-like
                t = getattr(v, "annotation", v)
            parts.append(f"{k}:{short_type_token(t)}")
        digest = sha1(",".join(parts).encode("utf-8")).hexdigest()[:10]
        return f"map:{digest}"

    def source(self) -> Any:
        return self.mapping


def as_shape(obj: Any) -> ModelShape:
    """Return a ModelShape wrapper for `obj`.

    - mapping → MappingShape
    - class → ClassShape
    - otherwise → InstanceShape
    """
    from collections.abc import Mapping as TMapping

    if isinstance(obj, TMapping):
        return MappingShape(obj)
    if isinstance(obj, type):
        return ClassShape(obj)
    return InstanceShape(obj)


def shape_id_token(obj: Any) -> str:
    """Stable identity token for objects supported by normalization."""
    return as_shape(obj).id_token()
