from duckdantic.normalize import normalize_fields
from duckdantic.fields import FieldOrigin, FieldAliasSet

class FakeFieldInfo:
    def __init__(self, annotation, alias=None, validation_alias=None, serialization_alias=None):
        self.annotation = annotation
        self.alias = alias
        self.validation_alias = validation_alias
        self.serialization_alias = serialization_alias

def test_mapping_of_fieldinfo_like():
    mapping = {
        "query": FakeFieldInfo(str, alias="q"),
        "lang": FakeFieldInfo(str, validation_alias=("language",)),
        "limit": FakeFieldInfo(int, serialization_alias=("max", "cap")),
    }
    fields = normalize_fields(mapping)
    assert fields["query"].origin is FieldOrigin.PYDANTIC
    assert fields["query"].alias == "q"
    assert fields["lang"].aliases and "language" in fields["lang"].aliases.validation
    assert fields["limit"].aliases and "max" in fields["limit"].aliases.serialization
