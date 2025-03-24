import dataclasses
import html

from yt_feed.models.errors import BadChannelException


@dataclasses.dataclass(frozen=True, eq=True)
class ChannelEntry:
    title: str
    desc: str
    thumbnail_url: str
    uploads: str


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
