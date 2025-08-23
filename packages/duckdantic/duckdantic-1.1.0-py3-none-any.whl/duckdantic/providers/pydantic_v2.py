from __future__ import annotations

from collections.abc import Mapping
from typing import Any, get_type_hints

from duckdantic.fields import FieldAliasSet, FieldOrigin, FieldView
from duckdantic.providers.base import Capabilities, FieldProvider


class PydanticV2Provider(FieldProvider):
    def can_handle(self, obj: Any) -> bool:
        return isinstance(obj, type) and isinstance(
            getattr(obj, "model_fields", None),
            Mapping,
        )

    def fields(self, obj: type) -> dict[str, FieldView]:
        mf = getattr(obj, "model_fields", None)
        out: dict[str, FieldView] = {}
        for name, val in mf.items():
            ann = getattr(val, "annotation", None)
            alias = getattr(val, "alias", None)
            val_alias = getattr(val, "validation_alias", None)
            ser_alias = getattr(val, "serialization_alias", None)

            def _as_tuple(x):
                if x is None:
                    return ()
                # Check for AliasChoices first
                choices = getattr(x, "choices", None)
                if choices is not None:
                    try:
                        return tuple(str(i) for i in choices)
                    except Exception:
                        pass
                if isinstance(x, list | tuple | set):
                    return tuple(str(i) for i in x)
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
                annotation=ann if ann is not None else object,
                alias=str(alias) if alias is not None else None,
                origin=FieldOrigin.PYDANTIC,
                aliases=aliases,
            )
        # computed
        mcf = getattr(obj, "model_computed_fields", None)
        if isinstance(mcf, Mapping):
            for name, cf in mcf.items():
                if name in out:
                    continue
                rt = getattr(cf, "return_type", None)
                if rt is None:
                    member = getattr(obj, name, None)
                    if member is not None:
                        fn = getattr(member, "fget", member)
                        try:
                            hints = get_type_hints(fn, include_extras=True)
                            rt = hints.get("return", object)
                        except Exception:
                            rt = object
                    else:
                        rt = object
                out[name] = FieldView(
                    name=name,
                    annotation=rt,
                    origin=FieldOrigin.PYDANTIC,
                )
        return out

    def required_map(self, obj: Any) -> dict[str, bool]:
        mf = getattr(obj, "model_fields", None) or {}
        out = {}
        for name, f in mf.items():
            out[name] = bool(getattr(f, "is_required", True))
        return out

    def computed(self, obj: Any) -> dict[str, type]:
        mcf = getattr(obj, "model_computed_fields", None)
        if not isinstance(mcf, Mapping):
            return {}
        ret: dict[str, type] = {}
        for name, cf in mcf.items():
            rt = getattr(cf, "return_type", None)
            if rt is None:
                member = getattr(obj, name, None)
                if member is not None:
                    fn = getattr(member, "fget", member)
                    try:
                        hints = get_type_hints(fn, include_extras=True)
                        rt = hints.get("return", object)
                    except Exception:
                        rt = object
                else:
                    rt = object
            ret[name] = rt
        return ret

    def capabilities(self, obj: Any) -> Capabilities:
        mcf = getattr(obj, "model_computed_fields", None)
        return Capabilities(
            has_required=True,
            has_aliases=True,
            has_computed=isinstance(mcf, Mapping),
            model_kind="pydantic-v2",
        )
