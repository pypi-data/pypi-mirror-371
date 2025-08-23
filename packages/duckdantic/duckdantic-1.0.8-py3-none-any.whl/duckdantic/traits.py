"""Declarative trait specifications for duckdantic."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FieldSpec:
    """Requirement for a single field.

    Args:
        name: Canonical field name.
        typ: Desired runtime type expression.
        required: Whether the field must be present.
        accept_alias: Whether name can be matched by alias.
        check_types: Whether to enforce type compatibility.
        custom_matcher: Optional override predicate: (actual, desired) -> bool.
    """

    name: str
    typ: Any
    required: bool = True
    accept_alias: bool = True
    check_types: bool = True
    custom_matcher: Callable[[Any, Any], bool] | None = None


@dataclass(frozen=True)
class TraitSpec:
    """A structural trait defined as a tuple of :class:`FieldSpec`.

    Args:
        name: Human-friendly identifier for the trait.
        fields: Tuple of field requirements.
        metadata: Free-form annotations for domain tags, notes, versions.
    """

    name: str
    fields: tuple[FieldSpec, ...]
    metadata: dict = field(default_factory=dict)
