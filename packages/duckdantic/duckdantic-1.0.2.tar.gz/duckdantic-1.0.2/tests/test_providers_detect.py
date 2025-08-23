import pytest
from duckdantic.providers.base import register_default_providers, registry

register_default_providers()

def test_mapping_provider_picks_mapping():
    prov = registry.pick({"x": int})
    assert prov is not None and prov.__class__.__name__.lower().startswith("mapping")

def test_plainclass_provider_picks_plain_annotations():
    class C:
        x: int
        y: list[str]
    prov = registry.pick(C)
    assert prov is not None and prov.__class__.__name__.lower().startswith("plainclass")
