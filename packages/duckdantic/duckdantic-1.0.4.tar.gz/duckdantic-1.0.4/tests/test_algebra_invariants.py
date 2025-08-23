from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.algebra import intersect, union, minus
from duckdantic.match import satisfies
from duckdantic.policy import POLICY_PRAGMATIC

class M:
    query: str
    lang: str
    limit: int

A = TraitSpec(name="A", fields=(FieldSpec("query", str),))
B = TraitSpec(name="B", fields=(FieldSpec("lang", str),))

def test_union_accepts_either():
    U = union(A, B, POLICY_PRAGMATIC)
    assert satisfies(M, U, POLICY_PRAGMATIC)  # M has both
    class OnlyA: query: str
    class OnlyB: lang: str
    assert satisfies(OnlyA, U, POLICY_PRAGMATIC)
    assert satisfies(OnlyB, U, POLICY_PRAGMATIC)

def test_intersect_requires_both():
    I = intersect(A, B, POLICY_PRAGMATIC)
    class OnlyA: query: str
    assert not satisfies(OnlyA, I, POLICY_PRAGMATIC)
    assert satisfies(M, I, POLICY_PRAGMATIC)

def test_minus_removes_fields():
    U = union(A, B, POLICY_PRAGMATIC)
    Mz = minus(U, A)
    # Mz should not require 'query' anymore
    class OnlyB: lang: str
    assert satisfies(OnlyB, Mz, POLICY_PRAGMATIC)
