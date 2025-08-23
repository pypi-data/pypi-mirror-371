from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies
from duckdantic.policy import POLICY_PRAGMATIC

class FakeFieldInfo:
    def __init__(self, annotation, alias=None, validation_alias=None, serialization_alias=None):
        self.annotation = annotation
        self.alias = alias
        self.validation_alias = validation_alias
        self.serialization_alias = serialization_alias

MODEL = {
    "query": FakeFieldInfo(str, alias="q"),
    "lang": FakeFieldInfo(str, validation_alias=("language",)),
}

def test_alias_and_validation_alias_match():
    trait1 = TraitSpec(name="QByName", fields=(FieldSpec("query", str, required=True, accept_alias=True),))
    assert satisfies(MODEL, trait1, POLICY_PRAGMATIC)

    trait2 = TraitSpec(name="QByAlias", fields=(FieldSpec("q", str, required=True, accept_alias=True),))
    assert satisfies(MODEL, trait2, POLICY_PRAGMATIC)

    trait3 = TraitSpec(name="LangByValidationAlias", fields=(FieldSpec("language", str, required=True, accept_alias=True),))
    assert satisfies(MODEL, trait3, POLICY_PRAGMATIC)
