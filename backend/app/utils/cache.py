# backend/app/utils/cache.py

import time
from threading import Lock

class SimpleCache:
    """A basic in-memory cache with TTL expiration."""
    def __init__(self):
        self._store = {}
        self._lock = Lock()

    def set(self, key, value, ttl_seconds: float = 60.0):
        expire_time = time.time() + ttl_seconds
        with self._lock:
            self._store[key] = (value, expire_time)

    def get(self, key):
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            value, expire_time = item
            if time.time() > expire_time:
                del self._store[key]
                return None
            return value

    def clear(self):
        with self._lock:
            self._store.clear()

# ✅ Global cache instance
cache = SimpleCache()
