import dataclasses
import datetime
import html

import isodate

from yt_feed.models.errors import BadChannelException


@dataclasses.dataclass(frozen=True, eq=True)
class ChannelEntry:
    title: str
    desc: str
    thumbnail_url: str
    uploads: str


@dataclasses.dataclass
class VideoEntry:
    title: str
    id: str
    desc: str
    published_at: str
    duration: str


def make_channel_entry(raw: dict) -> ChannelEntry:
    if raw.get("items"):
        title = html.escape(raw["items"][0]["snippet"]["title"])
        desc = html.escape(raw["items"][0]["snippet"]["description"])
        thumbnail_url = raw["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        uploads = raw["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return ChannelEntry(
            title=title, desc=desc, thumbnail_url=thumbnail_url, uploads=uploads
        )
    else:
        raise BadChannelException("No items returned, bad channel", "")


def make_video_entry(raw: dict) -> VideoEntry:
    title = html.escape(raw["snippet"]["title"])
    desc = html.escape(raw["snippet"]["description"])
    my_id = raw["id"]
    published_at_dt = datetime.datetime.strptime(
        raw["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
    )
    duration = isodate.parse_duration(raw["contentDetails"]["duration"])

    return VideoEntry(
        title=title,
        id=my_id,
        desc=desc,
        published_at=published_at_dt.strftime("%a, %d %b %Y %H:%M:%S +0000"),
        duration=duration,
    )


def parse_video_id(item: dict) -> str:
    return item["snippet"]["resourceId"]["videoId"]


def parse_channel_id(raw: list[dict]) -> str:
    return raw[0]["snippet"]["channelId"]
