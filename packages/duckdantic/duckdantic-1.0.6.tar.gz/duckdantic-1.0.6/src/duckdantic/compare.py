"""Trait comparison relations for duckdantic."""

from __future__ import annotations

from enum import Enum

from duckdantic.comparer import DefaultTypeComparer
from duckdantic.policy import TypeCompatPolicy
from duckdantic.traits import TraitSpec


class TraitRelation(Enum):
    """Relationship between two trait specifications."""

    EQUIVALENT = "equivalent"
    A_STRICTER_THAN_B = "a_stricter_than_b"
    B_STRICTER_THAN_A = "b_stricter_than_a"
    OVERLAPPING = "overlapping"
    DISJOINT = "disjoint"


def _implies(a: TraitSpec, b: TraitSpec, policy: TypeCompatPolicy) -> bool:
    cmp = DefaultTypeComparer()
    idx_a = {fs.name: fs for fs in a.fields}
    for fb in b.fields:
        fa = idx_a.get(fb.name)
        if fb.required and (not fa or not fa.required):
            return False
        if fb.check_types:
            if not fa or not fa.check_types:
                return False
            if not cmp.compatible(fa.typ, fb.typ, policy):
                return False
    return True


def compare_traits(
    a: TraitSpec,
    b: TraitSpec,
    policy: TypeCompatPolicy,
) -> TraitRelation:
    """Classify the relation of two traits under a policy.

    Heuristic for overlap/disjoint:
        - If neither implies the other but they share at least one field
          name, return OVERLAPPING; otherwise DISJOINT.
    """
    a_imp_b = _implies(a, b, policy)
    b_imp_a = _implies(b, a, policy)
    if a_imp_b and b_imp_a:
        return TraitRelation.EQUIVALENT
    if a_imp_b:
        return TraitRelation.A_STRICTER_THAN_B
    if b_imp_a:
        return TraitRelation.B_STRICTER_THAN_A
    names_a = {fs.name for fs in a.fields}
    names_b = {fs.name for fs in b.fields}
    return TraitRelation.OVERLAPPING if names_a & names_b else TraitRelation.DISJOINT
