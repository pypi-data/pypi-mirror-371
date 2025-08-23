from duckdantic.normalize import normalize_fields

class C:
    data: list[str]
    mapping: dict[str, int]

def test_instance_normalization_and_generics():
    inst = C()
    fields = normalize_fields(inst)
    assert fields["data"].annotation == list[str]
    assert fields["mapping"].annotation == dict[str, int]
