from typing import Optional, Union
from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies
from duckdantic.policy import TypeCompatPolicy, UnionBranchMode

class X:
    name: Optional[str]

def test_optional_satisfies_str_when_allowed():
    trait = TraitSpec(name="NeedsStr", fields=(FieldSpec("name", str, required=True, check_types=True),))
    policy = TypeCompatPolicy(allow_optional_widening=True)
    assert satisfies(X, trait, policy)

def test_union_on_desired_side():
    class Y: value: int
    trait = TraitSpec(name="IntOrStr", fields=(FieldSpec("value", Union[int, str], required=True, check_types=True),))
    policy = TypeCompatPolicy(allow_optional_widening=True, desired_union=UnionBranchMode.ANY)
    assert satisfies(Y, trait, policy)
