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
    url: str


@dataclasses.dataclass
class VideoEntry:
    title: str
    id: str
    desc: str
    published_at: str
    duration: str


def make_channel_entry(raw: dict, channel_url: str) -> ChannelEntry:
    """
    channel url is explicitly passed because if the feed elements are created from a channel or
    a user, we can just link the source url to the channel that uploaded the videos.
    If it is from a playlist, we want to link to the playlist itself.
    There might be a way to create the url from the elements given to us from youtube,
    but this seems more explicit.
    """
    if raw.get("items"):
        title = html.escape(raw["items"][0]["snippet"]["title"])
        desc = html.escape(raw["items"][0]["snippet"]["description"])
        thumbnail_url = raw["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        try:
            uploads = raw["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except KeyError:
            uploads = None
        return ChannelEntry(
            title=title,
            desc=desc,
            thumbnail_url=thumbnail_url,
            uploads=uploads,
            url=channel_url,
        )
    else:
        raise BadChannelException("No items returned, bad channel", "")


def make_video_entry(raw: dict) -> VideoEntry | None:
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

        return VideoEntry(
            title=title,
            id=my_id,
            desc=desc,
            published_at=published_at_dt.strftime("%a, %d %b %Y %H:%M:%S +0000"),
            duration=duration,
        )
    except KeyError:
        return None


def parse_video_id(item: dict) -> str:
    return item["snippet"]["resourceId"]["videoId"]


def parse_channel_id(raw: list[dict]) -> str:
    return raw[0]["snippet"]["channelId"]
