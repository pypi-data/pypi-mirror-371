from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies, explain
from duckdantic.policy import POLICY_PRAGMATIC

class N:
    query: str
    tags: list[str]

def test_type_checks_exact_and_generics():
    trait = TraitSpec(name="QTags", fields=(
        FieldSpec("query", str, required=True, check_types=True),
        FieldSpec("tags", list[str], required=True, check_types=True),
    ))
    assert satisfies(N, trait, POLICY_PRAGMATIC)

    bad = TraitSpec(name="BadTags", fields=(
        FieldSpec("tags", list[int], required=True, check_types=True),
    ))
    assert not satisfies(N, bad, POLICY_PRAGMATIC)
    exp = explain(N, bad, POLICY_PRAGMATIC)
    assert any("type mismatch" in r for r in exp["reasons"])
