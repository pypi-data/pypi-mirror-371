"""Trait set operations (intersect/union/minus) for duckdantic."""

from __future__ import annotations

from duckdantic.comparer import DefaultTypeComparer
from duckdantic.policy import TypeCompatPolicy
from duckdantic.traits import FieldSpec, TraitSpec


def intersect(a: TraitSpec, b: TraitSpec, policy: TypeCompatPolicy) -> TraitSpec:
    """Approximate intersection of two traits.

    Rules:
        - required := OR
        - check_types := OR
        - accept_alias := OR
        - type := meet (greatest lower bound); if incompatible → object
    """
    cmp = DefaultTypeComparer()
    idx_a = {f.name: f for f in a.fields}
    idx_b = {f.name: f for f in b.fields}
    names = set(idx_a) | set(idx_b)
    merged: dict[str, FieldSpec] = {}
    for name in names:
        fa, fb = idx_a.get(name), idx_b.get(name)
        if fa and fb:
            req = fa.required or fb.required
            chk = fa.check_types or fb.check_types
            alias = fa.accept_alias or fb.accept_alias
            typ = cmp.meet(fa.typ, fb.typ, policy) if chk else object
            merged[name] = FieldSpec(name, typ, req, alias, chk)
        else:
            f = fa or fb
            merged[name] = FieldSpec(
                f.name,
                f.typ,
                f.required,
                f.accept_alias,
                f.check_types,
            )
    return TraitSpec(
        name=f"intersect({a.name},{b.name})",
        fields=tuple(sorted(merged.values(), key=lambda x: x.name)),
    )


def union(a: TraitSpec, b: TraitSpec, policy: TypeCompatPolicy) -> TraitSpec:
    """Approximate union of two traits.

    A model should satisfy the union if it satisfies *either* input trait.

    Rules:
        - required := AND (missing field treated as False); i.e., fields present
          in only one trait become optional in the union.
        - check_types := OR
        - accept_alias := OR
        - type := join (least upper bound) heuristic
    """
    cmp = DefaultTypeComparer()
    idx_a = {f.name: f for f in a.fields}
    idx_b = {f.name: f for f in b.fields}
    names = set(idx_a) | set(idx_b)
    merged: dict[str, FieldSpec] = {}
    for name in names:
        fa, fb = idx_a.get(name), idx_b.get(name)
        if fa and fb:
            req = fa.required and fb.required
            chk = fa.check_types or fb.check_types
            alias = fa.accept_alias or fb.accept_alias
            typ = cmp.join(fa.typ, fb.typ, policy) if chk else object
            merged[name] = FieldSpec(name, typ, req, alias, chk)
        else:
            # Present in only one trait: optional in the union
            f = fa or fb
            req = False  # AND with missing => False
            chk = f.check_types
            alias = f.accept_alias
            typ = f.typ
            merged[name] = FieldSpec(f.name, typ, req, alias, chk)
    return TraitSpec(
        name=f"union({a.name},{b.name})",
        fields=tuple(sorted(merged.values(), key=lambda x: x.name)),
    )


def minus(a: TraitSpec, b: TraitSpec) -> TraitSpec:
    names_b = {f.name for f in b.fields}
    kept = [f for f in a.fields if f.name not in names_b]
    return TraitSpec(
        name=f"minus({a.name},{b.name})",
        fields=tuple(sorted(kept, key=lambda x: x.name)),
    )
