from typing import Annotated
from duckdantic.normalize import normalize_fields
from duckdantic.fields import FieldOrigin

class Plain:
    query: str
    tags: list[str]
    rating: Annotated[int, "0-5"]

def test_class_annotations():
    fields = normalize_fields(Plain)
    assert fields["query"].origin is FieldOrigin.ANNOTATION
    assert fields["tags"].annotation == list[str]
    assert str(fields["rating"].annotation).startswith("typing.Annotated")
