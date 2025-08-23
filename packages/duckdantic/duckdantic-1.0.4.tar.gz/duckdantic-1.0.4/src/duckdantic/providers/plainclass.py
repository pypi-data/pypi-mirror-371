from __future__ import annotations

from typing import Any, get_type_hints

from duckdantic.fields import FieldOrigin, FieldView
from duckdantic.providers.base import Capabilities, FieldProvider


class PlainClassProvider(FieldProvider):
    def can_handle(self, obj: Any) -> bool:
        return isinstance(obj, type)

    def fields(self, obj: type) -> dict[str, FieldView]:
        hints = get_type_hints(obj, include_extras=True)
        return {
            name: FieldView(
                name=name,
                annotation=ann,
                origin=FieldOrigin.ANNOTATION,
            )
            for name, ann in hints.items()
        }

    def required_map(self, obj: Any) -> dict[str, bool]:
        return {}

    def computed(self, obj: Any) -> dict[str, type]:
        return {}

    def capabilities(self, obj: Any) -> Capabilities:
        return Capabilities(
            has_required=False,
            has_aliases=False,
            has_computed=False,
            model_kind="plainclass",
        )
