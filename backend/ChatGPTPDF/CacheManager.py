from cachetools import TTLCache
import time
from .tasks import process_history_embedding
import debugpy
class CacheManager:
    _instance = None

    # def __init__(self, size=100, ttl=1800):
    #     self.cache = TTLCache(maxsize=size, ttl=ttl)
    #     self.key_access_time = {}  # 儲存每個 key 最後被存取的時間

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cache = TTLCache(maxsize=100, ttl=280)
            cls._instance.key_access_time = {}
        return cls._instance
        
    def get(self, key):
        value = self.cache.get(key)
        if value is not None:
            self.key_access_time[key] = time.monotonic()
        return value

    def set(self, key, value):
        self.cache[key] = value
        self.key_access_time[key] = time.monotonic()

    def delete(self, key):
        self.cache.pop(key, None)
        self.key_access_time.pop(key, None)

    def is_expired(self, key):
        if key not in self.cache:
            return True
        if time.monotonic() - self.key_access_time.get(key, 0) >= self.cache.ttl:
            return True
        return False

    def clear_expired(self):
        print(self.cache.keys())
        for key in list(self.cache.keys()):
            if self.is_expired(key):
                if key.startswith("HISTORY_KEY_"):
                    print("start process history embedding")
                    # 1. get cache data        
                    history = self.get(key)
                    messages = history.buffer
                    process_history_embedding.delay(key.replace("HISTORY_KEY_",""),messages)                       
                    self.delete(key)

    def cache_info(self):
        info = cachetools.CacheInfo(len(self.cache), self.cache.maxsize)
        info.hits = self.cache.hits
        info.misses = self.cache.misses
        info.expired = len([key for key in self.cache.keys() if self.is_expired(key)])
        return info
    
    def check_cache(self,key):
        if self.is_expired(key):
            self.delete(key)
            return False
        else:
            return True
