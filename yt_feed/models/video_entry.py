import dataclasses
import datetime
import html

import isodate


@dataclasses.dataclass
class VideoEntry:
    title: str
    id: str
    desc: str
    published_at: str
    duration: str


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
