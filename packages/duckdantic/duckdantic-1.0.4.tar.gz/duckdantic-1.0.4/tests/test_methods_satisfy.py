import pytest
from duckdantic import MethodSpec, methods_satisfy, methods_explain, POLICY_PRAGMATIC

class Good:
    def to_payload(self, n: int) -> dict:
        return {"n": n}

class BadMissing:
    pass

class BadParam:
    def to_payload(self, n: str) -> dict:  # wrong param type
        return {"n": n}

class BadReturn:
    def to_payload(self, n: int) -> list:  # wrong return type
        return [n]

spec = [MethodSpec("to_payload", params=[int], returns=dict)]

def test_good():
    assert methods_satisfy(Good, spec, POLICY_PRAGMATIC)
    assert methods_satisfy(Good(), spec, POLICY_PRAGMATIC)
    info = methods_explain(Good, spec, POLICY_PRAGMATIC)
    assert info["ok"] is True

def test_missing():
    assert not methods_satisfy(BadMissing, spec, POLICY_PRAGMATIC)
    info = methods_explain(BadMissing, spec, POLICY_PRAGMATIC)
    assert info["ok"] is False and "to_payload" in info["missing"]

def test_bad_param_and_return():
    assert not methods_satisfy(BadParam, spec, POLICY_PRAGMATIC)
    assert not methods_satisfy(BadReturn, spec, POLICY_PRAGMATIC)
    info_p = methods_explain(BadParam, spec, POLICY_PRAGMATIC)
    info_r = methods_explain(BadReturn, spec, POLICY_PRAGMATIC)
    assert info_p["param_conflicts"]
    assert info_r["return_conflicts"]