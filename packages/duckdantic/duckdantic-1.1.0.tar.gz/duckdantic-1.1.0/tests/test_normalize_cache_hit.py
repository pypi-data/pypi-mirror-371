from duckdantic.cache import normalize_fields_cached, get_cache_stats, clear_cache

class B:
    q: str
    n: int

def test_cache_hits_and_misses():
    clear_cache()
    stats0 = get_cache_stats()
    assert stats0["size"] == 0 and stats0["hits"] == 0 and stats0["misses"] == 0

    v1 = normalize_fields_cached(B)
    stats1 = get_cache_stats()
    assert stats1["size"] == 1 and stats1["misses"] == 1

    v2 = normalize_fields_cached(B)
    stats2 = get_cache_stats()
    assert stats2["hits"] >= 1
    # Same object mapping should be returned (identity), since we cache the dict
    assert v1 is v2
