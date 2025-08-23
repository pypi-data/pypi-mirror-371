from duckdantic.normalize import normalize_fields
from duckdantic.fields import FieldOrigin

class FakeFieldInfo:
    def __init__(self, annotation, alias=None):
        self.annotation = annotation
        self.alias = alias

class ModelLike:
    model_fields = {
        "query": FakeFieldInfo(str, alias="q"),
        "lang": FakeFieldInfo(str),
    }

def test_model_like():
    fields = normalize_fields(ModelLike)
    assert fields["query"].origin is FieldOrigin.PYDANTIC
    assert fields["query"].alias == "q"
    assert fields["lang"].annotation is str
