from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies, explain
from duckdantic.policy import TypeCompatPolicy, AliasMode

class FakeFieldInfo:
    def __init__(self, annotation, alias=None, validation_alias=None, serialization_alias=None):
        self.annotation = annotation
        self.alias = alias
        self.validation_alias = validation_alias
        self.serialization_alias = serialization_alias

MODEL = {
    "query": FakeFieldInfo(str, alias="q", validation_alias=("search",), serialization_alias=("qry",)),
    "lang": FakeFieldInfo(str, validation_alias=("language",), serialization_alias=("lng", "l")),
}

def test_allow_primary_only():
    policy = TypeCompatPolicy(alias_mode=AliasMode.ALLOW_PRIMARY)
    # 'q' should match 'query' via primary alias; others should not
    t1 = TraitSpec(name="ByPrimary", fields=(FieldSpec("q", str, required=True),))
    t2 = TraitSpec(name="ByValidation", fields=(FieldSpec("search", str, required=True),))
    t3 = TraitSpec(name="BySerialization", fields=(FieldSpec("qry", str, required=True),))
    assert satisfies(MODEL, t1, policy)
    assert not satisfies(MODEL, t2, policy)
    assert not satisfies(MODEL, t3, policy)

def test_use_validation_vs_serialization():
    t_val = TraitSpec(name="LangValidation", fields=(FieldSpec("language", str, required=True),))
    t_ser = TraitSpec(name="LangSerialization", fields=(FieldSpec("lng", str, required=True),))

    policy_val = TypeCompatPolicy(alias_mode=AliasMode.USE_VALIDATION)
    policy_ser = TypeCompatPolicy(alias_mode=AliasMode.USE_SERIALIZATION)

    assert satisfies(MODEL, t_val, policy_val)
    assert not satisfies(MODEL, t_val, policy_ser)

    assert satisfies(MODEL, t_ser, policy_ser)
    assert not satisfies(MODEL, t_ser, policy_val)

def test_alias_considered_in_explain():
    t = TraitSpec(name="NeedsLanguage", fields=(FieldSpec("language", str, required=True),))
    policy = TypeCompatPolicy(alias_mode=AliasMode.USE_BOTH)
    info = explain(MODEL, t, policy)
    # alias_considered for 'language' should include the alias 'language' from the model
    assert "language" in info["alias_considered"]
    assert "language" in info["alias_considered"]["language"]
