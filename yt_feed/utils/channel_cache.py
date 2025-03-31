from flask_caching import Cache

cache_config = {
    "CACHE_TYPE": "SimpleCache",
    # 5 minute cache
    "CACHE_DEFAULT_TIMEOUT": 300,
}

flask_cache = Cache()
