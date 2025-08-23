"""Trait matching (satisfies/explain) for duckdantic."""

from __future__ import annotations

from typing import Any

from duckdantic.comparer import DefaultTypeComparer
from duckdantic.fields import FieldView
from duckdantic.normalize import normalize_fields
from duckdantic.policy import AliasMode, TypeCompatPolicy
from duckdantic.traits import FieldSpec, TraitSpec


def _iter_alias_strings(fv: FieldView, mode: AliasMode) -> list[str]:
    """Yield alias strings for a field in a deterministic order based on.

    mode.
    """
    seen: list[str] = []
    primary = None
    if fv.alias is not None:
        primary = str(fv.alias)
    if fv.aliases and fv.aliases.primary and (primary is None):
        primary = fv.aliases.primary
    validation = list(fv.aliases.validation) if fv.aliases else []
    serialization = list(fv.aliases.serialization) if fv.aliases else []

    if mode == AliasMode.DISALLOW:
        return seen
    if mode == AliasMode.ALLOW_PRIMARY:
        if primary is not None and primary not in seen:
            seen.append(primary)
        return seen
    if mode == AliasMode.USE_VALIDATION:
        seen.extend([a for a in validation if a not in seen])
        return seen
    if mode == AliasMode.USE_SERIALIZATION:
        seen.extend([a for a in serialization if a not in seen])
        return seen
    if mode == AliasMode.USE_BOTH:
        seen.extend([a for a in validation if a not in seen])
        seen.extend([a for a in serialization if a not in seen])
        if primary is not None and primary not in seen:
            seen.append(primary)
        return seen
    if mode == AliasMode.PREFER_VALIDATION:
        seen.extend([a for a in validation if a not in seen])
        seen.extend([a for a in serialization if a not in seen])
        if primary is not None and primary not in seen:
            seen.append(primary)
        return seen
    if mode == AliasMode.PREFER_SERIALIZATION:
        seen.extend([a for a in serialization if a not in seen])
        seen.extend([a for a in validation if a not in seen])
        if primary is not None and primary not in seen:
            seen.append(primary)
        return seen
    return seen


def _resolve_field(
    spec: FieldSpec,
    fields: dict[str, FieldView],
    *,
    alias_mode: AliasMode,
    alias_considered: dict | None = None,
) -> FieldView | None:
    # 1) Direct name match
    fv = fields.get(spec.name)
    if fv is not None:
        return fv
    # 2) Alias lookup per policy
    if not spec.accept_alias or alias_mode == AliasMode.DISALLOW:
        return None
    for f in fields.values():
        aliases = _iter_alias_strings(f, alias_mode)
        if alias_considered is not None:
            alias_considered.setdefault(spec.name, [])
            for a in aliases:
                if a not in alias_considered[spec.name]:
                    alias_considered[spec.name].append(a)
        if spec.name in aliases:
            return f
    return None


def satisfies(obj: Any, trait: TraitSpec, policy: TypeCompatPolicy) -> bool:
    """Return True if `obj` satisfies the trait under the policy.

    Args:
        obj: Class, instance, or mapping to inspect.
        trait: Structural requirements.
        policy: Comparison policy for type checks.
    """
    fields = normalize_fields(obj)
    cmp = DefaultTypeComparer()
    for fs in trait.fields:
        fv = _resolve_field(fs, fields, alias_mode=policy.alias_mode)
        if fv is None:
            if fs.required:
                return False
            continue
        if fs.check_types:
            ok = (
                fs.custom_matcher(fv.annotation, fs.typ)
                if fs.custom_matcher
                else cmp.compatible(
                    fv.annotation,
                    fs.typ,
                    policy,
                )
            )
            if not ok:
                return False
    return True


def explain(obj: Any, trait: TraitSpec, policy: TypeCompatPolicy) -> dict:
    """Explain why `obj` satisfies or fails `trait` under `policy`.

    Returns:
        dict: {
            'ok': bool,
            'reasons': list[str],  # backward-compat summary
            'evidence': {name: {actual, desired}},
            'missing': list[str],
            'type_conflicts': [{'name', 'actual', 'desired', 'why'}],
            'alias_considered': {spec_name: [alias, ...]}
        }
    """
    fields = normalize_fields(obj)
    cmp = DefaultTypeComparer()
    reasons: list[str] = []
    evidence: dict[str, dict] = {}
    missing: list[str] = []
    type_conflicts: list[dict] = []
    alias_considered: dict[str, list[str]] = {}
    ok = True
    for fs in trait.fields:
        fv = _resolve_field(
            fs,
            fields,
            alias_mode=policy.alias_mode,
            alias_considered=alias_considered,
        )
        if fv is None:
            if fs.required:
                ok = False
                missing.append(fs.name)
                reasons.append(f"missing required field '{fs.name}'")
            continue
        if fs.check_types:
            good = (
                fs.custom_matcher(fv.annotation, fs.typ)
                if fs.custom_matcher
                else cmp.compatible(
                    fv.annotation,
                    fs.typ,
                    policy,
                )
            )
            if not good:
                ok = False
                why = cmp.explain(fv.annotation, fs.typ, policy)
                reasons.append(f"type mismatch for '{fs.name}'")
                evidence[fs.name] = {
                    "actual": str(
                        fv.annotation,
                    ),
                    "desired": str(fs.typ),
                }
                type_conflicts.append(
                    {
                        "name": fs.name,
                        "actual": str(
                            fv.annotation,
                        ),
                        "desired": str(fs.typ),
                        "why": why,
                    },
                )
    return {
        "ok": ok,
        "reasons": reasons,
        "evidence": evidence,
        "missing": missing,
        "type_conflicts": type_conflicts,
        "alias_considered": alias_considered,
    }
