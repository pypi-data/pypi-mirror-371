from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from duckdantic.fields import FieldAliasSet, FieldOrigin, FieldView
from duckdantic.providers.base import Capabilities, FieldProvider


class MappingProvider(FieldProvider):
    def can_handle(self, obj: Any) -> bool:
        return isinstance(obj, Mapping)

    def fields(self, obj: Mapping[str, Any]) -> dict[str, FieldView]:
        out: dict[str, FieldView] = {}
        for name, val in obj.items():
            if isinstance(val, FieldView):
                out[name] = val
                continue
            ann = getattr(val, "annotation", None)
            if ann is not None:
                alias = getattr(val, "alias", None)
                val_alias = getattr(val, "validation_alias", None)
                ser_alias = getattr(val, "serialization_alias", None)

                def _as_tuple(x):
                    if x is None:
                        return ()
                    if isinstance(x, list | tuple | set):
                        return tuple(str(i) for i in x)
                    choices = getattr(x, "choices", None)
                    if choices is not None:
                        try:
                            return tuple(str(i) for i in choices)
                        except Exception:
                            pass
                    if hasattr(x, "__iter__") and not isinstance(x, str | bytes):
                        try:
                            return tuple(str(i) for i in x)
                        except Exception:
                            pass
                    return (str(x),)

                aliases = None
                if alias is not None or val_alias is not None or ser_alias is not None:
                    aliases = FieldAliasSet(
                        primary=str(alias) if alias is not None else None,
                        validation=_as_tuple(val_alias),
                        serialization=_as_tuple(ser_alias),
                    )
                out[name] = FieldView(
                    name=name,
                    annotation=ann,
                    alias=str(alias) if alias is not None else None,
                    origin=FieldOrigin.PYDANTIC,
                    aliases=aliases,
                )
            else:
                out[name] = FieldView(
                    name=name,
                    annotation=val,
                    origin=FieldOrigin.ADHOC,
                )
        return out

    def required_map(self, obj: Any) -> dict[str, bool]:
        return {}

    def computed(self, obj: Any) -> dict[str, type]:
        return {}

    def capabilities(self, obj: Any) -> Capabilities:
        return Capabilities(
            has_required=False,
            has_aliases=True,
            has_computed=False,
            model_kind="mapping",
        )
