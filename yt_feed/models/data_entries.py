import dataclasses
import datetime
import html
from typing import Any
from typing import Self

import isodate

from yt_feed.models.errors import BadChannelException


@dataclasses.dataclass(frozen=True, eq=True)
class ChannelEntry:
    title: str
    desc: str
    thumbnail_url: str
    url: str

    @classmethod
    def construct(cls, raw: dict[str, Any], wanted_url) -> "ChannelEntry":
        """
        Accepts either a YT API response dict or a hand-made dict and constructs ChannelEntry.
        """
        normalized = _normalize_channel_dict(raw, wanted_url)
        return cls(**normalized)


@dataclasses.dataclass(frozen=True, eq=True)
class VideoEntry:
    title: str
    id: str
    desc: str
    published_at: str
    duration: str

    @classmethod
    def construct(cls, raw: dict[str, Any]) -> Self | None:
        normalized = _normalize_video_entry(raw)
        if normalized:
            return cls(**normalized)
        return None


def _normalize_channel_dict(raw: dict[str, Any], wanted_url: str) -> dict[str, str]:
    """
    Normalizes either:
      - YT API dict: {"items": [...], ...}
      - Manual dict: {"title": ...}
    into: {"title", "desc", "thumbnail_url", "uploads", "url"}
    """
    if raw.get("items"):
        title = html.escape(raw["items"][0]["snippet"]["title"])
        desc = html.escape(raw["items"][0]["snippet"]["description"])
        thumbnail_url = raw["items"][0]["snippet"]["thumbnails"]["high"]["url"]

    else:
        title = raw.get("title")
        desc = raw.get("desc") or raw.get("description")
        thumbnail_url = raw.get("thumbnail_url")

    if not title or desc is None:
        raise BadChannelException("No items returned, bad channel", "")

    return {
        "title": title,
        "desc": desc,
        "thumbnail_url": thumbnail_url,
        "url": wanted_url,
    }


def _normalize_video_entry(raw: dict) -> dict[str, str] | None:
    # todo if this video is a short, don't return it?
    # currently there is not a good way from the data returned to see if is a short.
    try:
        title = html.escape(raw["snippet"]["title"])
        desc = html.escape(raw["snippet"]["description"])
        my_id = raw["id"]
        published_at_dt = datetime.datetime.strptime(
            raw["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
        )
        duration = isodate.parse_duration(raw["contentDetails"]["duration"])

        return {
            "title": title,
            "id": my_id,
            "desc": desc,
            "published_at": published_at_dt.strftime("%a, %d %b %Y %H:%M:%S +0000"),
            "duration": duration,
        }
    except KeyError:
        return None


def parse_playlist_info(item: dict) -> dict[str, str]:
    return {
        "title": f"{item['snippet']['title']} - {item['snippet']['channelTitle']}",
        "desc": item["snippet"]["description"],
        "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
    }


def parse_video_id(item: dict) -> str:
    return item["snippet"]["resourceId"]["videoId"]


def parse_channel_id(raw: list[dict]) -> str:
    return raw[0]["snippet"]["channelId"]
