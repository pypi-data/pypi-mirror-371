from duckdantic import FieldSpec, TraitSpec, abc_for, duckisinstance, duckissubclass, POLICY_PRAGMATIC

Searchable = TraitSpec("Searchable", (FieldSpec("query", str, required=True, check_types=True),))
SearchableABC = abc_for(Searchable)

class Good:
    query: str

class Bad:
    query: int

def test_issubclass_isinstance():
    assert issubclass(Good, SearchableABC)
    assert isinstance(Good(), SearchableABC)
    assert not issubclass(Bad, SearchableABC)

def test_duck_helpers():
    assert duckissubclass(Good, Searchable, POLICY_PRAGMATIC)
    assert duckisinstance(Good(), Searchable, POLICY_PRAGMATIC)