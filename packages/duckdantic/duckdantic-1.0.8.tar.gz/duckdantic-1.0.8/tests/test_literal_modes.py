from typing import Literal
from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies
from duckdantic.policy import TypeCompatPolicy, LiteralMode

class S:
    lang: Literal["en"]

class T:
    lang: str

def test_literal_exact_subset_and_reject_plain_type():
    trait = TraitSpec(name="LangEnOrFr", fields=(FieldSpec("lang", Literal["en","fr"]),))
    # exact: S is Literal["en"] which is subset of desired -> ok
    policy_exact = TypeCompatPolicy(literal_mode=LiteralMode.EXACT)
    assert satisfies(S, trait, policy_exact)
    # plain str should NOT satisfy an exact literal set
    assert not satisfies(T, trait, policy_exact)

def test_literal_coerce_to_base():
    trait = TraitSpec(name="LangStr", fields=(FieldSpec("lang", Literal["en","fr"]),))
    policy_base = TypeCompatPolicy(literal_mode=LiteralMode.COERCE_TO_BASE)
    # desired literal coerces to base str, so T(str) satisfies
    assert satisfies(T, trait, policy_base)
