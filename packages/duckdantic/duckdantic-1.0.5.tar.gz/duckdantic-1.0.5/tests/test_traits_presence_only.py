from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies, explain
from duckdantic.policy import POLICY_PRAGMATIC

class M:
    query: str

def test_required_and_optional_fields_by_name():
    trait = TraitSpec(name="QOnly", fields=(
        FieldSpec("query", str, required=True, check_types=False),
        FieldSpec("lang", str, required=False, check_types=False),
    ))
    assert satisfies(M, trait, POLICY_PRAGMATIC)  # lang optional
    info = explain(M, trait, POLICY_PRAGMATIC)
    assert info["ok"] is True
