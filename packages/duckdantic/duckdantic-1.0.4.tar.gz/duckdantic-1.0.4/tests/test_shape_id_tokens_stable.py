from duckdantic.shapes import shape_id_token
from duckdantic.normalize import normalize_fields

class A:
    x: int
    y: list[str]

def test_class_token_stable_across_calls():
    t1 = shape_id_token(A)
    t2 = shape_id_token(A)
    assert t1 == t2
    # normalizing should not change the token
    normalize_fields(A)
    t3 = shape_id_token(A)
    assert t1 == t3

def test_mapping_token_independent_of_order():
    mapping1 = {"x": int, "y": list[str]}
    mapping2 = {"y": list[str], "x": int}
    assert shape_id_token(mapping1) == shape_id_token(mapping2)
