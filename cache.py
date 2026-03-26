# 9. LRUCache class — thread-safe, generic
#    - __init__(capacity)
#    - get(key) — returns value or None
#    - put(key, value)
#    - invalidate(key)
#    - clear()
#    - size property
#    - Thread safety: concurrent get/put from multiple threads must not corrupt state

from collections import OrderedDict
import threading


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock: # lock ensures that only one thread is modifying the cache at a time
            '''
            you might ask why we have self.lock in get (since get appears to be an access fn only), 
            we are moving the accessed key to the end, which is a write operation
            this is why lock is necessary, bc we are making updates to the cache
            '''
            if key not in self.cache:
                return None

            # move to end --> most recently used
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                # update + move to end
                self.cache.move_to_end(key)

            self.cache[key] = value

            # remove if over capacity
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False) 

    def invalidate(self, key):
        with self.lock:
            if key in self.cache:
                del self.cache[key]

    def clear(self):
        with self.lock:
            self.cache.clear()

    @property
    def size(self):
        with self.lock:
            return len(self.cache)