from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies
from duckdantic.policy import TypeCompatPolicy

class N1:
    n: int

class N2:
    n: float

def test_int_to_float_and_complex():
    trait_float = TraitSpec(name="NeedsFloat", fields=(FieldSpec("n", float),))
    trait_complex = TraitSpec(name="NeedsComplex", fields=(FieldSpec("n", complex),))
    policy = TypeCompatPolicy(allow_numeric_widening=True)
    assert satisfies(N1, trait_float, policy)
    assert satisfies(N1, trait_complex, policy)
    assert satisfies(N2, trait_complex, policy)
