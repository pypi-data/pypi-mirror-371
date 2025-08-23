from __future__ import annotations

from duckdantic.build.trait_builder import TraitBuilder


def trait_from_model(
    model_cls,
    *,
    include_computed=True,
    use_required_if_pydantic=True,
    accept_alias=True,
    check_types=True,
    name=None,
):
    tb = (
        TraitBuilder.from_model(model_cls)
        .include_computed(include_computed)
        .respect_required(use_required_if_pydantic)
        .accept_aliases(accept_alias)
        .check_types(check_types)
    )
    if name:
        tb = tb.name(name)
    return tb.build()
