import sys
from typing import TypedDict, NotRequired, Required
from duckdantic.normalize import normalize_fields

class UserTD(TypedDict, total=False):
    id: Required[int]
    name: str  # total=False makes this NotRequired by default
    email: NotRequired[str]

def test_typeddict_unwrap_required_notrequired():
    fields = normalize_fields(UserTD)
    # keys present
    assert {"id", "name", "email"} <= set(fields.keys())
    # annotations unwrapped
    assert fields["id"].annotation is int
    assert fields["name"].annotation is str
    assert fields["email"].annotation is str
