from __future__ import annotations

from typing import Any, get_args, get_origin

from duckdantic.fields import FieldOrigin, FieldView
from duckdantic.providers.base import Capabilities, FieldProvider


def _strip_required_optional(t: Any) -> Any:
    try:
        from typing import NotRequired, Required  # type: ignore
    except Exception:  # pragma: no cover
        Required = object  # type: ignore
        NotRequired = object  # type: ignore
    o = get_origin(t)
    if o in (Required, NotRequired):
        args = get_args(t)
        return args[0] if args else Any
    if (
        o is not None
        and getattr(
            o,
            "__qualname__",
            str(o),
        ).endswith("Required")
    ) or getattr(o, "__qualname__", str(o)).endswith("NotRequired"):
        args = get_args(t)
        return args[0] if args else Any
    return t


class TypedDictProvider(FieldProvider):
    def can_handle(self, obj: Any) -> bool:
        return isinstance(obj, type) and (
            hasattr(obj, "__required_keys__")
            or hasattr(
                obj,
                "__optional_keys__",
            )
        )

    def fields(self, obj: type) -> dict[str, FieldView]:
        ann = getattr(obj, "__annotations__", {}) or {}
        return {
            name: FieldView(
                name=name,
                annotation=_strip_required_optional(t),
                origin=FieldOrigin.ANNOTATION,
            )
            for name, t in ann.items()
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
            model_kind="typeddict",
        )
