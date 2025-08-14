from flask import Response
from flask_caching import Cache

cache_config = {
    "CACHE_TYPE": "SimpleCache",
    # 5 minute cache
    "CACHE_DEFAULT_TIMEOUT": 300,
}


def only_200(response: Response):
    return response.status_code == 200


flask_cache = Cache()
