from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies
from duckdantic.policy import POLICY_PRAGMATIC

class FakeFieldInfo:
    def __init__(self, annotation):
        self.annotation = annotation

class RootLike:
    model_fields = {"root": FakeFieldInfo(str)}

def test_root_trait():
    trait = TraitSpec(name="RootString", fields=(FieldSpec("root", str, required=True, check_types=True),))
    assert satisfies(RootLike, trait, POLICY_PRAGMATIC)
