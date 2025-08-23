from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from duckdantic.fields import FieldView


@dataclass(frozen=True)
class Capabilities:
    has_required: bool
    has_aliases: bool
    has_computed: bool
    # e.g., "pydantic-v2", "dataclass", "typeddict", "mapping", "plainclass", "attrs"
    model_kind: str


class FieldProvider(Protocol):
    def can_handle(self, obj: Any) -> bool: ...
    def fields(self, obj: Any) -> dict[str, FieldView]: ...

    def required_map(
        self,
        obj: Any,
    ) -> dict[str, bool]: ...  # empty if not known

    def computed(
        # name -> return type (only extras)
        self,
        obj: Any,
    ) -> dict[str, type]: ...

    def capabilities(self, obj: Any) -> Capabilities: ...


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: list[tuple[int, FieldProvider]] = []

    def add(self, provider: FieldProvider, *, priority: int = 100) -> None:
        self._providers.append((priority, provider))
        self._providers.sort(key=lambda x: x[0])

    def pick(self, obj: Any) -> FieldProvider | None:
        for _prio, p in self._providers:
            try:
                if p.can_handle(obj):
                    return p
            except Exception:
                continue
        return None

    def clear(self) -> None:
        self._providers.clear()


registry = ProviderRegistry()

_defaults_added = False


def register_default_providers() -> None:
    global _defaults_added
    if _defaults_added:
        return
    from duckdantic.providers.attrs import AttrsProvider
    from duckdantic.providers.dataclass import DataclassProvider
    from duckdantic.providers.mapping import MappingProvider
    from duckdantic.providers.plainclass import PlainClassProvider
    from duckdantic.providers.pydantic_v2 import PydanticV2Provider
    from duckdantic.providers.typeddict import TypedDictProvider

    registry.add(PydanticV2Provider(), priority=10)
    registry.add(DataclassProvider(), priority=20)
    registry.add(TypedDictProvider(), priority=30)
    registry.add(AttrsProvider(), priority=40)
    registry.add(MappingProvider(), priority=90)
    registry.add(PlainClassProvider(), priority=100)
    _defaults_added = True
