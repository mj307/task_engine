# 9. LRUCache class — thread-safe, generic
#    - __init__(capacity)
#    - get(key) — returns value or None
#    - put(key, value)
#    - invalidate(key)
#    - clear()
#    - size property
#    - Thread safety: concurrent get/put from multiple threads must not corrupt state

import threading
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None

            value = self.cache.pop(key)
            self.cache[key] = value
            return value

    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)

            elif len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)

            self.cache[key] = value