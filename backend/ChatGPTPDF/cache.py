from cachetools import TTLCache
from datetime import datetime, timedelta

# Define a global cache with a maximum size of 1000 and a TTL of 30 minutes
cache = TTLCache(maxsize=100, ttl=1800)

# Function to get a value from the cache
def get_from_cache(key):
    return cache.get(key)

# Function to set a value in the cache
def set_in_cache(key, value):
    cache[key] = value

# Function to delete a value from the cache
def delete_from_cache(key):
    del cache[key]

# Function to clear the cache
def clear_cache():
    cache.clear()

# Function to check if a key is in the cache and if it has expired
def is_expired(key):
    if key in cache:
        value = cache[key]
        if isinstance(value, tuple) and len(value) >= 2:
            last_accessed_time = value[1]
            if datetime.now() - last_accessed_time > timedelta(minutes=30):
                return True
            else:
                return False
        else:
            return False
    else:
        return False
# The following code checks if a key is in the cache and if it has expired. If the key is in the cache and has not expired, it returns False. If the key is in the cache and has expired, it deletes the key from the cache and returns True. If the key is not in the cache, it returns False.

def check_cache(key):
    if is_expired(key):
        delete_from_cache(key)
        return True
    else:
        return False

# The above function can be used to check if a key is in the cache and if it has expired 
#     before retrieving the value from the cache. If the key has expired, the value will be deleted from the cache and the function can retrieve the value from another source.
# The above function can be used to check if a key is in the cache and if it has expired. 
# If the key is in the cache and has not expired, it returns False. 
# If the key is in the cache and has expired, it deletes the key from the cache and returns True. 
# If the key is not in the cache, it returns False.
# To check if a key is in the cache and has expired, call the check_cache function with the key as the argument.
# If the function returns True, the key has expired and should be removed from the cache. If it returns False, the key is still valid in the cache. 
