from collections.abc import Sequence
from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies
from duckdantic.policy import TypeCompatPolicy, ContainerOriginMode

class L:
    xs: list[str]

def test_sequence_covariant_under_relaxed_origin():
    trait = TraitSpec(name="SeqObject", fields=(FieldSpec("xs", Sequence[object]),))
    policy = TypeCompatPolicy(container_origin_mode=ContainerOriginMode.RELAXED_PROTOCOL)
    assert satisfies(L, trait, policy)
