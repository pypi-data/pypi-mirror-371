from duckdantic.normalize import normalize_fields

class FakeFieldInfo:
    def __init__(self, annotation):
        self.annotation = annotation

class RootLike:
    model_fields = {"root": FakeFieldInfo(str)}

def test_root_like():
    fields = normalize_fields(RootLike)
    assert "root" in fields
    assert fields["root"].annotation is str
