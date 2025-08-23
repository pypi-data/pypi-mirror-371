from typing import Annotated
from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies
from duckdantic.policy import TypeCompatPolicy, AnnotatedHandling

class A1:
    rating: Annotated[int, "0-5"]

class A2:
    rating: Annotated[int, "1-10"]

class APlain:
    rating: int

def test_annotated_strict_equal_metadata():
    trait = TraitSpec(name="RatingStrict", fields=(FieldSpec("rating", Annotated[int, "0-5"]),))
    policy = TypeCompatPolicy(annotated_handling=AnnotatedHandling.STRICT)
    assert satisfies(A1, trait, policy)
    assert not satisfies(A2, trait, policy)  # meta differs
    assert not satisfies(APlain, trait, policy)  # missing Annotated on actual
