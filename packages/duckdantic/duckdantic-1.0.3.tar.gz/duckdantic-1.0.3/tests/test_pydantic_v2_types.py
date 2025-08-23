import pytest
try:
    import pydantic as pyd
except Exception:
    pytestmark = pytest.mark.skip(reason="pydantic not installed")

from typing import Optional, Literal
from duckdantic.traits import FieldSpec, TraitSpec
from duckdantic.match import satisfies
from duckdantic.policy import TypeCompatPolicy, LiteralMode

class N(pyd.BaseModel):
    tags: list[str]
    count: Optional[int] = None
    lang: Literal["en"] = "en"

def test_list_and_optional_and_literal():
    t = TraitSpec(name="Mix", fields=(
        FieldSpec("tags", list[str], required=True, check_types=True),
        FieldSpec("count", int, required=False, check_types=True),
        FieldSpec("lang", Literal["en","fr"], required=True, check_types=True),
    ))
    # Optional widening on count; literal exact subset for lang
    policy = TypeCompatPolicy(literal_mode=LiteralMode.EXACT)
    assert satisfies(N, t, policy)
