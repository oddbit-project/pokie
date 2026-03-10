import pickle
import time

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
        self.expiry = {}
        self.prefix = ""

    def set_prefix(self, prefix):
        self.prefix = prefix if prefix else ""

    def _key(self, key):
        return self.prefix + key if self.prefix else key

    def _is_expired(self, key):
        if key in self.expiry:
            if time.monotonic() >= self.expiry[key]:
                del self.cache[key]
                del self.expiry[key]
                return True
        return False

    def get(self, key):
        key = self._key(key)
        if key not in self.cache or self._is_expired(key):
            return None
        return pickle.loads(self.cache.get(key))

    def set(self, key, value, ttl=None):
        key = self._key(key)
        self.cache[key] = pickle.dumps(value)
        if ttl and ttl > 0:
            self.expiry[key] = time.monotonic() + ttl
        elif key in self.expiry:
            del self.expiry[key]

    def has(self, key):
        key = self._key(key)
        if self._is_expired(key):
            return False
        return key in self.cache

    def remove(self, key):
        key = self._key(key)
        if key in self.cache:
            del self.cache[key]
        if key in self.expiry:
            del self.expiry[key]

    def purge(self):
        self.cache = {}
        self.expiry = {}
