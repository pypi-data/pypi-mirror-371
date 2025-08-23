import pytest
try:
    import pydantic as pyd
except Exception:
    pytestmark = pytest.mark.skip(reason="pydantic not installed")

from duckdantic.normalize import normalize_fields
from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies
from duckdantic.policy import TypeCompatPolicy, AliasMode

class M(pyd.BaseModel):
    query: str = pyd.Field(alias="q", validation_alias=pyd.AliasChoices("search"), serialization_alias="qry")
    lang: str = pyd.Field(validation_alias=pyd.AliasChoices("language"), serialization_alias="lng")

def test_normalize_model_fields_real_pydantic():
    fields = normalize_fields(M)
    assert "query" in fields and fields["query"].alias == "q"
    assert fields["lang"].aliases and "language" in fields["lang"].aliases.validation

def test_alias_modes_against_real_pydantic():
    t_primary = TraitSpec(name="ByPrimary", fields=(FieldSpec("q", str, required=True),))
    assert satisfies(M, t_primary, TypeCompatPolicy(alias_mode=AliasMode.ALLOW_PRIMARY))

    t_val = TraitSpec(name="ByValidation", fields=(FieldSpec("language", str, required=True),))
    assert satisfies(M, t_val, TypeCompatPolicy(alias_mode=AliasMode.USE_VALIDATION))

    t_ser = TraitSpec(name="BySerialization", fields=(FieldSpec("lng", str, required=True),))
    assert satisfies(M, t_ser, TypeCompatPolicy(alias_mode=AliasMode.USE_SERIALIZATION))
