"""Type compatibility policies for duckdantic."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class UnionBranchMode(Enum):
    """How to evaluate unions when comparing type expressions."""

    ANY = auto()
    ALL = auto()


class ContainerOriginMode(Enum):
    """How strictly to compare container origins (e.g., list vs Sequence)."""

    EXACT = auto()
    RELAXED_PROTOCOL = auto()


class AnnotatedHandling(Enum):
    """Treatment of typing.Annotated metadata during comparison."""

    STRIP = auto()
    STRICT = auto()


class LiteralMode(Enum):
    """How to treat typing.Literal during comparison."""

    EXACT = auto()
    COERCE_TO_BASE = auto()


class AliasMode(Enum):
    """Whether and how aliases may satisfy name requirements."""

    DISALLOW = auto()
    ALLOW_PRIMARY = auto()
    USE_VALIDATION = auto()
    USE_SERIALIZATION = auto()
    USE_BOTH = auto()
    PREFER_VALIDATION = auto()
    PREFER_SERIALIZATION = auto()


@dataclass(frozen=True)
class TypeCompatPolicy:
    """Configuration influencing type compatibility decisions.

    Attributes:
        allow_optional_widening: If True, permit Optional[T] to satisfy T.
        allow_numeric_widening: If True, permit int to satisfy float, etc.
        desired_union: Branch mode for unions on the desired side.
        actual_union: Branch mode for unions on the actual side.
        container_origin_mode: Whether to relax list/tuple/set/dict origins to ABCs.
        annotated_handling: Whether to strip Annotated metadata.
        literal_mode: Whether to coerce Literal[...] to its base type.
        alias_mode: Alias resolution mode (primary, validation, serialization).
    """

    allow_optional_widening: bool = True
    allow_numeric_widening: bool = True
    desired_union: UnionBranchMode = UnionBranchMode.ANY
    actual_union: UnionBranchMode = UnionBranchMode.ANY
    container_origin_mode: ContainerOriginMode = ContainerOriginMode.RELAXED_PROTOCOL
    annotated_handling: AnnotatedHandling = AnnotatedHandling.STRIP
    literal_mode: LiteralMode = LiteralMode.COERCE_TO_BASE
    alias_mode: AliasMode = AliasMode.USE_BOTH


# Default pragmatic policy used by tests
POLICY_PRAGMATIC = TypeCompatPolicy()
