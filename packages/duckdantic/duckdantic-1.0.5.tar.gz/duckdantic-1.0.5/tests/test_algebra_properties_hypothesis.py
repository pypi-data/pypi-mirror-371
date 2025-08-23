
import pytest

try:
    from hypothesis import given, strategies as st
except Exception:
    pytestmark = pytest.mark.skip(reason="hypothesis not installed")
else:
    from duckdantic.traits import FieldSpec, TraitSpec
    from duckdantic.algebra import union, intersect
    from duckdantic.compare import compare_traits, TraitRelation
    from duckdantic.policy import POLICY_PRAGMATIC

    base_types = st.sampled_from([int, float, str])
    list_types = st.sampled_from([list[int], list[str]])
    types_strat = st.one_of(base_types, list_types)

    name_strat = st.sampled_from(["a", "b", "c", "x", "y", "z"])

    def trait_strat():
        return st.lists(
            st.tuples(name_strat, types_strat, st.booleans()),
            min_size=1, max_size=3,
            unique_by=lambda x: x[0]  # Ensure unique field names
        ).map(lambda items: TraitSpec(
            name="T",
            fields=tuple(FieldSpec(n, t, required=req, check_types=True) for (n, t, req) in items)
        ))

    @given(a=trait_strat(), b=trait_strat())
    def test_union_commutative(a, b):
        u1 = union(a, b, POLICY_PRAGMATIC)
        u2 = union(b, a, POLICY_PRAGMATIC)
        assert compare_traits(u1, u2, POLICY_PRAGMATIC) == TraitRelation.EQUIVALENT

    @given(a=trait_strat())
    def test_union_idempotent(a):
        u = union(a, a, POLICY_PRAGMATIC)
        assert compare_traits(u, a, POLICY_PRAGMATIC) == TraitRelation.EQUIVALENT

    @given(a=trait_strat(), b=trait_strat())
    def test_intersect_commutative(a, b):
        i1 = intersect(a, b, POLICY_PRAGMATIC)
        i2 = intersect(b, a, POLICY_PRAGMATIC)
        assert compare_traits(i1, i2, POLICY_PRAGMATIC) == TraitRelation.EQUIVALENT

    @given(a=trait_strat())
    def test_intersect_idempotent(a):
        i = intersect(a, a, POLICY_PRAGMATIC)
        assert compare_traits(i, a, POLICY_PRAGMATIC) == TraitRelation.EQUIVALENT
