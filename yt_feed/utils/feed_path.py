import re
from urllib.parse import parse_qs
from urllib.parse import urlparse

_YT_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
_SHORT_HOSTS = {"youtu.be", "www.youtu.be"}

_ID = re.compile(r"[\w.-]+")
_CHANNEL_ID = re.compile(r"UC[\w-]{22}")
_PLAYLIST_ID = re.compile(r"(PL|UU|OL|FL)[\w-]{10,}")


def _valid(value: str | None, pattern: re.Pattern = _ID) -> str | None:
    return value if value and pattern.fullmatch(value) else None


def _from_bare(value: str) -> str | None:
    """Handle input that is just an id or handle, not a url."""
    if value.startswith("@") and _valid(value[1:]):
        return f"/c/{value}"
    if _valid(value, _CHANNEL_ID):
        return f"/u/{value}"
    if _valid(value, _PLAYLIST_ID):
        return f"/p/{value}"
    return None


def feed_path_for(raw: str) -> str | None:
    """
    Turn a pasted YouTube url (or bare handle / id) into the matching yt_feed path.

    Returns None if the input isn't something we know how to serve.
    """
    value = raw.strip()
    if not value:
        return None
    if bare := _from_bare(value):
        return bare

    if "://" not in value:
        value = f"https://{value}"
    url = urlparse(value)
    host = (url.hostname or "").lower()
    segments = [s for s in url.path.split("/") if s]
    query = parse_qs(url.query)

    if host in _SHORT_HOSTS:
        video_id = _valid(segments[0] if segments else None)
        return f"/dl/{video_id}.m4a" if video_id else None
    if host not in _YT_HOSTS or not segments:
        return None

    first, rest = segments[0], segments[1:]
    # a playlist beats a video, since the user probably wants the whole feed
    if playlist_id := _valid(query.get("list", [None])[0]):
        return f"/p/{playlist_id}"
    if first == "watch":
        video_id = _valid(query.get("v", [None])[0])
        return f"/dl/{video_id}.m4a" if video_id else None
    if first.startswith("@") and _valid(first[1:]):
        return f"/c/{first}"
    if first == "channel" and rest and _valid(rest[0], _CHANNEL_ID):
        return f"/u/{rest[0]}"
    if first == "c" and rest and _valid(rest[0].removeprefix("@")):
        return f"/c/{rest[0]}"
    return None
