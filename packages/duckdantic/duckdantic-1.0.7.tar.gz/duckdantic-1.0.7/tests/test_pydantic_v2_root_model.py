import pytest
try:
    import pydantic as pyd
except Exception:
    pytestmark = pytest.mark.skip(reason="pydantic not installed")

from duckdantic.normalize import normalize_fields
from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies
from duckdantic.policy import POLICY_PRAGMATIC

class UserId(pyd.RootModel[str]):
    pass

def test_root_model_normalizes_root():
    fields = normalize_fields(UserId)
    assert "root" in fields and fields["root"].annotation is str

def test_trait_on_root():
    trait = TraitSpec(name="RootStr", fields=(FieldSpec("root", str),))
    assert satisfies(UserId, trait, POLICY_PRAGMATIC)
