from duckdantic.normalize import normalize_fields
from duckdantic.fields import FieldOrigin

def test_mapping_of_types_basic():
    fields = normalize_fields({"query": str, "limit": int})
    assert set(fields.keys()) == {"query", "limit"}
    assert fields["query"].annotation is str
    assert fields["query"].origin is FieldOrigin.ADHOC
    assert fields["limit"].annotation is int
