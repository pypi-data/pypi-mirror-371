"""Pragmatic type comparer for duckdantic traits."""

from __future__ import annotations

from collections.abc import Mapping, Sequence, Set
from typing import Annotated, Any, Literal, get_args, get_origin

from duckdantic.policy import (
    AnnotatedHandling,
    ContainerOriginMode,
    LiteralMode,
    TypeCompatPolicy,
    UnionBranchMode,
)

_Any = Any


class DefaultTypeComparer:
    """Covers Optional/Union, Annotated, Literal, basic containers, numeric.

    widening.

    The comparer works on runtime typing objects (e.g., ``list[str]``, ``Annotated[int, ...]``).
    It is intentionally conservative and configurable via :class:`TypeCompatPolicy`.
    """

    # -------- public API --------

    def compatible(self, actual: Any, desired: Any, policy: TypeCompatPolicy) -> bool:
        a = self._normalize(actual, policy)
        d = self._normalize(desired, policy)
        return self._compat(a, d, policy)

    def join(self, a: Any, b: Any, policy: TypeCompatPolicy) -> Any:
        """Least upper bound (very approximate).

        If a <: b, return b; if b <: a, return a; else return object.
        """
        if self.compatible(a, b, policy):
            return b
        if self.compatible(b, a, policy):
            return a
        return object

    def meet(self, a: Any, b: Any, policy: TypeCompatPolicy) -> Any:
        """Greatest lower bound (very approximate).

        If a <: b, return a; if b <: a, return b; else return object.
        """
        if self.compatible(a, b, policy):
            return a
        if self.compatible(b, a, policy):
            return b
        return object

    # -------- normalization --------

    def _normalize(self, t: Any, policy: TypeCompatPolicy) -> Any:
        o = get_origin(t)
        # Strip Annotated wrapper when policy requires
        if policy.annotated_handling == AnnotatedHandling.STRIP and o is Annotated:
            return get_args(t)[0]
        # Coerce Literal[...] to base type when policy requires
        if policy.literal_mode == LiteralMode.COERCE_TO_BASE and o is Literal:
            args = get_args(t)
            if args:
                return type(args[0])
        return t

    # -------- core compatibility --------

    def _compat(self, a: Any, d: Any, policy: TypeCompatPolicy) -> bool:
        # Top type
        if a is _Any or d is _Any:
            return True

        # Equality or subclass
        if a == d:
            return True
        try:
            if isinstance(a, type) and isinstance(d, type) and issubclass(a, d):
                return True
        except TypeError:
            # Parametrized generics are not classes
            pass

        ao, do = get_origin(a), get_origin(d)

        # Annotated STRICT: require both sides to be Annotated with equal metadata; compare bases
        if policy.annotated_handling == AnnotatedHandling.STRICT:
            if ao is Annotated and do is Annotated:
                a_base, *a_meta = get_args(a)
                d_base, *d_meta = get_args(d)
                if a_meta != d_meta:
                    return False
                return self._compat(a_base, d_base, policy)
            # one side Annotated but not the other → reject under STRICT
            if (ao is Annotated) != (do is Annotated):
                return False

        # Literal EXACT: desired Literal[...] requires actual Literal subset
        if policy.literal_mode == LiteralMode.EXACT:
            if do is Literal:
                d_vals = set(get_args(d))
                if ao is Literal:
                    a_vals = set(get_args(a))
                    return a_vals.issubset(d_vals)
                # Plain types cannot guarantee literal membership
                return False
            # Allow a Literal[T] to satisfy base desired (e.g., Literal[1] -> int)
            if ao is Literal and do is not Literal:
                a_vals = get_args(a)
                if not a_vals:
                    return False
                base = type(a_vals[0])
                try:
                    if isinstance(do, type) and issubclass(base, do):
                        return True
                except TypeError:
                    pass
                # Else continue into generic logic below

        # Union/Optional handling
        if self._is_union(ao):
            branches = get_args(a)
            res = [self._compat(b, d, policy) for b in branches]
            return any(res) if policy.actual_union == UnionBranchMode.ANY else all(res)
        if self._is_union(do):
            branches = get_args(d)
            res = [self._compat(a, b, policy) for b in branches]
            return any(res) if policy.desired_union == UnionBranchMode.ANY else all(res)

        # Optional widening
        if policy.allow_optional_widening:
            if self._is_optional(a) and not self._is_optional(d):
                return any(self._compat(x, d, policy) for x in get_args(a))
            if self._is_optional(d) and not self._is_optional(a):
                return any(self._compat(a, x, policy) for x in get_args(d))

        # Numeric widening chain: int -> float -> complex
        if (
            policy.allow_numeric_widening
            and isinstance(a, type)
            and isinstance(d, type)
        ):
            if a is int and d in (float, complex, object):
                return True
            if a is float and d in (complex, object):
                return True
            if a is int and d is complex:
                return True

        # Parametrized containers
        if ao and do:
            ao2, do2 = self._relax(ao, policy), self._relax(do, policy)
            if ao2 != do2:
                return False
            a_args, d_args = get_args(a), get_args(d)
            # If desired is unparameterized, accept origin match
            if not d_args:
                return True
            if len(a_args) != len(d_args):
                return False
            # Treat Sequence[...] as covariant in its parameter under relaxed origin
            if ao2 is Sequence:
                return all(
                    self._compat(ax, dx, policy)
                    for ax, dx in zip(a_args, d_args, strict=False)
                )
            # Default: invariant-ish comparison via recursive compat
            return all(
                self._compat(ax, dx, policy)
                for ax, dx in zip(a_args, d_args, strict=False)
            )

        return False

    # -------- small helpers --------

    @staticmethod
    def _is_union(origin: object | None) -> bool:
        from types import UnionType
        from typing import Union

        return origin in (Union, UnionType)

    @staticmethod
    def _is_optional(t: Any) -> bool:
        o = get_origin(t)
        if not DefaultTypeComparer._is_union(o):
            return False
        return type(None) in get_args(t)

    @staticmethod
    def _relax(o: object, policy: TypeCompatPolicy) -> object:
        if policy.container_origin_mode == ContainerOriginMode.EXACT:
            return o
        mapping = {
            list: Sequence,
            tuple: Sequence,
            set: Set,
            frozenset: Set,
            dict: Mapping,
        }
        return mapping.get(o, o)

    # --- reason helper ---
    def explain(self, actual: Any, desired: Any, policy: TypeCompatPolicy) -> str:
        """Return a short reason why `actual` is not compatible with `desired`.

        Best-effort diagnostic for explain() payloads.
        """
        a = self._normalize(actual, policy)
        d = self._normalize(desired, policy)
        if a == d:
            return "types are equal"
        ao, do = get_origin(a), get_origin(d)
        if ao and do:
            ao2, do2 = self._relax(ao, policy), self._relax(do, policy)
            if ao2 != do2:
                return f"container origin mismatch: {getattr(ao, '__name__', ao)} vs {getattr(do, '__name__', do)}"
            a_args, d_args = get_args(a), get_args(d)
            if len(a_args) != len(d_args):
                return f"container arity mismatch: {len(a_args)} vs {len(d_args)}"
            for i, (ax, dx) in enumerate(zip(a_args, d_args, strict=False)):
                if not self._compat(ax, dx, policy):
                    return f"element {i} mismatch: {ax} vs {dx}"
        # Optional/Union differences
        if self._is_optional(a) and not self._is_optional(d):
            return "actual is Optional but desired is non-Optional"
        if self._is_optional(d) and not self._is_optional(a):
            return "desired is Optional but actual is non-Optional"
        return "not compatible under current policy"
