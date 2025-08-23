"""Normalize classes, instances, and mappings into `FieldView`s.

The `normalize_fields` function is the first step of duckdantic: given a
variety of inputs, it returns a uniform mapping of field names to FieldViews.

Supported inputs:
    - Mapping[str, type] (ad-hoc annotations)
    - Mapping[str, FieldInfo-like] (duck-typed: has `.annotation`, optional `.alias`)
    - Mapping[str, FieldView] (already normalized)
    - Class with `model_fields: dict[str, FieldInfo-like]` (Pydantic v2 duck-typed)
    - TypedDict classes (unwrap Required/NotRequired to base types)
    - dataclasses (class only)
    - attrs classes (class only; skipped if attrs not installed)
    - Class with `__annotations__` (plain)
    - Instance (delegates to its class)

Notes:
    We do NOT import Pydantic here. We duck-type its `FieldInfo` and
    `model_fields` so this module works even without pydantic installed.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, get_args, get_origin, get_type_hints

from duckdantic.fields import FieldAliasSet, FieldOrigin, FieldView


def _from_mapping(mapping: Mapping[str, Any]) -> dict[str, FieldView]:
    out: dict[str, FieldView] = {}
    for name, val in mapping.items():
        # Already a FieldView
        if isinstance(val, FieldView):
            out[name] = val
            continue
        # FieldInfo-like: has .annotation (and maybe .alias / validation_alias / serialization_alias)
        ann = getattr(val, "annotation", None)
        if ann is not None:
            alias = getattr(val, "alias", None)
            # collect pydantic v2-style alias buckets if present
            val_alias = getattr(val, "validation_alias", None)
            ser_alias = getattr(val, "serialization_alias", None)
            aliases = None

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
                if isinstance(x, list | tuple):
                    return tuple(str(i) for i in x)
                return (str(x),)

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
            continue
        # Plain type
        out[name] = FieldView(
            name=name,
            annotation=val,
            origin=FieldOrigin.ADHOC,
        )
    return out


def _strip_required_optional(t: Any) -> Any:
    """Return underlying type if `t` is Required[T] or NotRequired[T]."""
    try:
        from typing import NotRequired, Required  # type: ignore
    except Exception:  # pragma: no cover
        Required = object  # type: ignore
        NotRequired = object  # type: ignore
    o = get_origin(t)
    if o in (Required, NotRequired):
        args = get_args(t)
        return args[0] if args else Any
    # Fallback: detect by name to be resilient
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


def _from_class(cls: type) -> dict[str, FieldView]:
    # Pydantic v2 duck-typed model_fields
    model_fields = getattr(cls, "model_fields", None)
    if isinstance(model_fields, Mapping):
        return _from_mapping(model_fields)

    # TypedDict detection: classes produced by typing.TypedDict have __required_keys__/__optional_keys__
    is_typed_dict = hasattr(cls, "__required_keys__") or hasattr(
        cls,
        "__optional_keys__",
    )
    if is_typed_dict:
        ann = getattr(cls, "__annotations__", {}) or {}
        out: dict[str, FieldView] = {}
        for name, t in ann.items():
            out[name] = FieldView(
                name=name,
                annotation=_strip_required_optional(
                    t,
                ),
                origin=FieldOrigin.ANNOTATION,
            )
        return out

    # dataclass detection
    try:
        import dataclasses

        if dataclasses.is_dataclass(cls):
            hints = get_type_hints(cls, include_extras=True)
            return {
                name: FieldView(
                    name=name,
                    annotation=ann,
                    origin=FieldOrigin.ANNOTATION,
                )
                for name, ann in hints.items()
            }
    except Exception:
        pass

    # attrs detection: presence of __attrs_attrs__
    if hasattr(cls, "__attrs_attrs__"):
        hints = get_type_hints(cls, include_extras=True)
        return {
            name: FieldView(
                name=name,
                annotation=ann,
                origin=FieldOrigin.ANNOTATION,
            )
            for name, ann in hints.items()
        }

    # Plain annotations
    hints = get_type_hints(cls, include_extras=True)
    return {
        name: FieldView(
            name=name,
            annotation=ann,
            origin=FieldOrigin.ANNOTATION,
        )
        for name, ann in hints.items()
    }


def normalize_fields(obj: Any) -> dict[str, FieldView]:
    """Return a mapping of field name → FieldView from diverse inputs.

    Args:
        obj: A class, an instance, or a mapping representing fields.

    Returns:
        dict[str, FieldView]: Canonical field views for downstream reasoning.

    Raises:
        TypeError: If `obj` cannot be interpreted as a fields source.
    """
    # Mapping
    if isinstance(obj, Mapping):
        return _from_mapping(obj)
    # Class
    if isinstance(obj, type):
        return _from_class(obj)
    # Instance
    if not isinstance(obj, str | bytes) and hasattr(obj, "__class__"):
        return _from_class(obj.__class__)
    raise TypeError(
        "Unsupported input for normalize_fields: expected mapping, class, or instance",
    )
