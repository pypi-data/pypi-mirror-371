import pytest
try:
    import attr  # attrs library
except Exception:
    attr = None  # type: ignore

from duckdantic.normalize import normalize_fields
from duckdantic.fields import FieldOrigin

@pytest.mark.skipif(attr is None, reason="attrs not installed")
def test_attrs_class_supported():
    @attr.define
    class A:
        query: str
        tags: list[str]

    fields = normalize_fields(A)
    assert fields["query"].origin is FieldOrigin.ANNOTATION
    assert fields["tags"].annotation == list[str]
