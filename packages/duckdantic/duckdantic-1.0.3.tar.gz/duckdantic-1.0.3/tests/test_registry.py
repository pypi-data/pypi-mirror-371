from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.registry import TraitRegistry
from duckdantic.policy import POLICY_PRAGMATIC

class Model:
    query: str
    limit: int

def test_registry_find_compatible():
    reg = TraitRegistry()
    t1 = TraitSpec(name="Search", fields=(FieldSpec("query", str),))
    t2 = TraitSpec(name="Limited", fields=(FieldSpec("limit", int),))
    t3 = TraitSpec(name="Other", fields=(FieldSpec("lang", str),))

    for t in (t1, t2, t3):
        reg.add(t)

    result = reg.find_compatible(Model, POLICY_PRAGMATIC)
    assert result["Search"] is True
    assert result["Limited"] is True
    assert result["Other"] is False
