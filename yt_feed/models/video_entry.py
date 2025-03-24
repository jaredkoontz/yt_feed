import dataclasses
import html


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
    published_at = raw["snippet"]["publishedAt"]
    duration = raw["contentDetails"]["duration"]
    return VideoEntry(
        title=title,
        id=my_id,
        desc=desc,
        published_at=published_at,
        duration=duration,
    )
