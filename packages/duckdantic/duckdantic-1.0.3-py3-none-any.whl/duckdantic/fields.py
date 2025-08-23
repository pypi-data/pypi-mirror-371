"""Canonical field representations (backend-agnostic)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class FieldOrigin(Enum):
    """Where a field description came from."""

    PYDANTIC = "pydantic"
    ANNOTATION = "annotation"
    ADHOC = "adhoc"


@dataclass(frozen=True)
class FieldAliasSet:
    """Aliases for a field (Pydantic v2-aware, but duck-typed)."""

    primary: str | None = None
    validation: tuple[str, ...] = ()
    serialization: tuple[str, ...] = ()

    def all(self) -> tuple[str, ...]:
        prim = (self.primary,) if self.primary is not None else tuple()
        return tuple(prim) + tuple(self.validation) + tuple(self.serialization)


@dataclass(frozen=True)
class FieldView:
    """Canonical, backend-agnostic view of a single field."""

    name: str
    annotation: Any
    alias: str | None = None
    origin: FieldOrigin = FieldOrigin.ADHOC
    aliases: FieldAliasSet | None = None
