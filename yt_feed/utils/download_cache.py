import time
from urllib.parse import parse_qs
from urllib.parse import urlparse

from yt_feed.utils.channel_cache import flask_cache

"""
Resolving a video's audio url means a full yt-dlp extraction, which is slow and
memory hungry. YouTube hands back a temporary url that stays good for hours, so we
hold on to it: a podcatcher that probes a url before fetching it, retries, or
resumes a download only pays for one extraction instead of one per request.
"""

_KEY_PREFIX = "dl_url"

# Used when a url does not advertise an expiry of its own. Comfortably inside the
# lifetime YouTube currently hands out.
_FALLBACK_TIMEOUT = 3600

# Let go of a url early, so a download that starts on a cache hit still has time to
# finish before YouTube stops honoring it.
_EXPIRY_MARGIN = 900

# Never trust advertised expiry past this, however far out it claims to be.
_MAX_TIMEOUT = 21600


def _cache_key(video_id: str) -> str:
    return f"{_KEY_PREFIX}:{video_id}"


def _advertised_expiry(url: str) -> int | None:
    """
    yt urls carry the unix timestamp they stop working at in an `expire`
    query param. Returns None when it is absent or unparseable.
    """
    try:
        query = urlparse(url).query
    except ValueError:
        # urlparse rejects a handful of malformed urls outright
        return None
    expire = parse_qs(query).get("expire", [""])[0]
    try:
        return int(expire)
    except ValueError:
        return None


def cache_timeout(url: str, now: float | None = None) -> int:
    """
    How many seconds we are willing to serve `url` from cache. Zero means the url is
    already too close to expiring to be worth keeping.
    """
    now = time.time() if now is None else now
    expiry = _advertised_expiry(url)
    if expiry is None:
        return _FALLBACK_TIMEOUT
    remaining = int(expiry - now - _EXPIRY_MARGIN)
    return max(0, min(remaining, _MAX_TIMEOUT))


def cached_audio_url(video_id: str) -> str | None:
    return flask_cache.get(_cache_key(video_id))


def cache_audio_url(video_id: str, url: str) -> None:
    timeout = cache_timeout(url)
    # Handing back an expired url is worse than doing the extraction again.
    if timeout > 0:
        flask_cache.set(_cache_key(video_id), url, timeout=timeout)
