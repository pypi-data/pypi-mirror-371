from duckdantic.naming import short_type_token, auto_name

def test_short_type_token_and_auto_name():
    token = short_type_token(list[str])
    assert token == "list[str]"
    nm1 = auto_name("Trait", [("query", str), ("tags", list[str])])
    nm2 = auto_name("Trait", [("query", str), ("tags", list[str])])
    assert nm1 == nm2
    assert nm1.startswith("Trait_query_tags__")
