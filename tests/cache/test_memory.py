from pokie.cache import MemoryCache


class TestMemoryCache:

    def test_mutability(self, pokie_di):
        cache = MemoryCache(pokie_di)
        key = "key1"
        data = {"key": "value"}
        assert cache.has(key) is False
        cache.set(key, data)
        assert cache.has(key) is True
        # mutate stored object
        data["key"] = 3

        # test for cache immutability
        record = cache.get(key)
        assert record is not None
        assert record["key"] == "value"

    def test_get_nonexistent(self, pokie_di):
        cache = MemoryCache(pokie_di)
        assert cache.get("nonexistent") is None

    def test_set_get_roundtrip(self, pokie_di):
        cache = MemoryCache(pokie_di)
        cache.set("key", "value")
        assert cache.get("key") == "value"

    def test_has(self, pokie_di):
        cache = MemoryCache(pokie_di)
        assert cache.has("key") is False
        cache.set("key", "value")
        assert cache.has("key") is True

    def test_remove(self, pokie_di):
        cache = MemoryCache(pokie_di)
        cache.set("key", "value")
        assert cache.has("key") is True
        cache.remove("key")
        assert cache.has("key") is False

    def test_remove_nonexistent(self, pokie_di):
        cache = MemoryCache(pokie_di)
        cache.remove("nonexistent")  # should not raise

    def test_purge(self, pokie_di):
        cache = MemoryCache(pokie_di)
        cache.set("key1", "val1")
        cache.set("key2", "val2")
        assert cache.has("key1") is True
        assert cache.has("key2") is True
        cache.purge()
        assert cache.has("key1") is False
        assert cache.has("key2") is False

    def test_set_with_ttl(self, pokie_di):
        cache = MemoryCache(pokie_di)
        cache.set("key", "value", ttl=60)
        assert cache.get("key") == "value"

    def test_complex_values(self, pokie_di):
        cache = MemoryCache(pokie_di)
        data = {"nested": {"list": [1, 2, 3], "dict": {"a": "b"}}}
        cache.set("complex", data)
        result = cache.get("complex")
        assert result == data
        assert result["nested"]["list"] == [1, 2, 3]
