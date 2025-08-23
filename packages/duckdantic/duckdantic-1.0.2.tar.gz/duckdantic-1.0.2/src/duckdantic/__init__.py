"""Duckdantic - Flexible structural typing and runtime validation for Python.

Duckdantic provides a powerful way to define structural types (traits) and check
whether objects satisfy them at runtime, without requiring inheritance or type
annotations. It works seamlessly with Pydantic, dataclasses, TypedDict, and
plain Python objects.

Key Features:
    - Structural typing based on object shape, not inheritance
    - Works with any Python object type
    - Flexible type policies for customizable validation
    - High-performance with intelligent caching
    - ABC integration for isinstance/issubclass support
    - Method signature checking
    - Trait composition with set operations

Basic Usage:
    >>> from duckdantic import TraitSpec, FieldSpec, satisfies
    >>>
    >>> # Define a trait
    >>> PersonTrait = TraitSpec(
    ...     name="Person",
    ...     fields=(
    ...         FieldSpec("name", str, required=True),
    ...         FieldSpec("age", int, required=True),
    ...     )
    ... )
    >>>
    >>> # Check if objects satisfy the trait
    >>> person = {"name": "Alice", "age": 30}
    >>> assert satisfies(person, PersonTrait)

Duck API (Recommended):
    >>> from pydantic import BaseModel
    >>> from duckdantic import Duck
    >>>
    >>> class User(BaseModel):
    ...     name: str
    ...     email: str
    >>>
    >>> UserDuck = Duck(User)
    >>>
    >>> # Use with isinstance
    >>> data = {"name": "Bob", "email": "bob@example.com"}
    >>> assert isinstance(data, UserDuck)
"""

from __future__ import annotations

from duckdantic.adapters.abc import abc_for, duckisinstance, duckissubclass
from duckdantic.algebra import intersect, minus, union
from duckdantic.build.methods import MethodSpec, methods_explain, methods_satisfy
from duckdantic.cache import clear_cache, get_cache_stats, normalize_fields_cached
from duckdantic.compare import TraitRelation, compare_traits
from duckdantic.fields import FieldAliasSet, FieldOrigin, FieldView
from duckdantic.match import explain, satisfies
from duckdantic.models import (
    Duck,
    DuckModel,
    DuckRootModel,
    DuckType,
    as_duck,
    is_duck_of,
)
from duckdantic.naming import auto_name, short_type_token
from duckdantic.normalize import normalize_fields
from duckdantic.policy import POLICY_PRAGMATIC, AliasMode, TypeCompatPolicy
from duckdantic.registry import TraitRegistry
from duckdantic.shapes import ShapeOrigin, shape_id_token
from duckdantic.traits import FieldSpec, TraitSpec

__all__ = [
    "POLICY_PRAGMATIC",
    "AliasMode",
    "Duck",
    "DuckModel",
    "DuckRootModel",
    "DuckType",
    "FieldAliasSet",
    "FieldOrigin",
    "FieldSpec",
    "FieldView",
    "MethodSpec",
    "ShapeOrigin",
    "TraitRegistry",
    "TraitRelation",
    "TraitSpec",
    "TypeCompatPolicy",
    "abc_for",
    "as_duck",
    "auto_name",
    "clear_cache",
    "compare_traits",
    "duckisinstance",
    "duckissubclass",
    "explain",
    "get_cache_stats",
    "intersect",
    "is_duck_of",
    "methods_explain",
    "methods_satisfy",
    "minus",
    "normalize_fields",
    "normalize_fields_cached",
    "satisfies",
    "shape_id_token",
    "short_type_token",
    "union",
]
__version__ = "0.0.3"
