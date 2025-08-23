from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import explain
from duckdantic.policy import TypeCompatPolicy

class M:
    tags: list[int]

def test_explain_has_type_conflicts_and_why():
    trait = TraitSpec(name="StrTags", fields=(FieldSpec("tags", list[str], required=True, check_types=True),))
    info = explain(M, trait, TypeCompatPolicy())
    assert info["ok"] is False
    assert info["type_conflicts"], "expected a type_conflicts list"
    conflict = info["type_conflicts"][0]
    assert conflict["name"] == "tags"
    assert "why" in conflict and isinstance(conflict["why"], str) and conflict["why"]
    # keep backwards-compatible reasons list too
    assert any("type mismatch" in r for r in info["reasons"])
