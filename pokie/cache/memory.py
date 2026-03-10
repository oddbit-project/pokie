import pickle

from rick.base import Di
from rick.mixin import Injectable
from rick.resource import CacheInterface


class MemoryCache(CacheInterface, Injectable):
    """
    In-memory cache

    Note: This cache implementation is for unit testing purposes only; DO NOT use it for regular development or
     production!!!
    """

    def __init__(self, di: Di):
        super().__init__(di)
        self.cache = {}
        self.prefix = ""

    def set_prefix(self, prefix):
        self.prefix = prefix if prefix else ""

    def _key(self, key):
        return self.prefix + key if self.prefix else key

    def get(self, key):
        key = self._key(key)
        if key not in self.cache:
            return None
        return pickle.loads(self.cache.get(key))

    def set(self, key, value, ttl=None):
        self.cache[self._key(key)] = pickle.dumps(value)

    def has(self, key):
        return self._key(key) in self.cache

    def remove(self, key):
        key = self._key(key)
        if key in self.cache:
            del self.cache[key]

    def purge(self):
        self.cache = {}
