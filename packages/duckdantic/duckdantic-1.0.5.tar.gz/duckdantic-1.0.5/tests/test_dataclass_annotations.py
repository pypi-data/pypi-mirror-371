from dataclasses import dataclass
from typing import Annotated
from duckdantic.normalize import normalize_fields
from duckdantic.fields import FieldOrigin

@dataclass
class Record:
    query: str
    tags: list[str]
    rating: Annotated[int, "0-5"]

def test_dataclass_is_supported():
    fields = normalize_fields(Record)
    assert fields["query"].origin is FieldOrigin.ANNOTATION
    assert fields["tags"].annotation == list[str]
    assert str(fields["rating"].annotation).startswith("typing.Annotated")
