from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.policy import POLICY_PRAGMATIC
from duckdantic.compare import compare_traits, TraitRelation

A = TraitSpec(name="A", fields=(FieldSpec("query", str),))
B = TraitSpec(name="B", fields=(FieldSpec("query", str),))

Strict = TraitSpec(name="Strict", fields=(FieldSpec("query", str), FieldSpec("lang", str)))
Loose = TraitSpec(name="Loose", fields=(FieldSpec("query", str),))

Incomp1 = TraitSpec(name="Incomp1", fields=(FieldSpec("query", str),))
Incomp2 = TraitSpec(name="Incomp2", fields=(FieldSpec("query", int),))

def test_equivalent():
    assert compare_traits(A, B, POLICY_PRAGMATIC) == TraitRelation.EQUIVALENT

def test_stricter():
    assert compare_traits(Strict, Loose, POLICY_PRAGMATIC) == TraitRelation.A_STRICTER_THAN_B
    assert compare_traits(Loose, Strict, POLICY_PRAGMATIC) == TraitRelation.B_STRICTER_THAN_A

def test_overlapping_vs_disjoint():
    # Share a field name but incompatible types -> overlapping (by heuristic)
    assert compare_traits(Incomp1, Incomp2, POLICY_PRAGMATIC) == TraitRelation.OVERLAPPING
    # Disjoint names -> disjoint
    D1 = TraitSpec(name="D1", fields=(FieldSpec("a", int),))
    D2 = TraitSpec(name="D2", fields=(FieldSpec("b", int),))
    assert compare_traits(D1, D2, POLICY_PRAGMATIC) == TraitRelation.DISJOINT
