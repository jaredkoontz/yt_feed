import datetime
import os

import isodate
from flask import render_template

from yt_feed.models.channel_entry import ChannelEntry
from yt_feed.models.video_entry import VideoEntry
from yt_feed.utils.youtube_api_call import yt_videos


def _fix_datetimes(item: VideoEntry) -> None:
    d = datetime.datetime.strptime(item.published_at, "%Y-%m-%dT%H:%M:%SZ")
    item.published_at = d.strftime("%a, %d %b %Y %H:%M:%S +0000")

    duration_iso = item.duration
    item.duration = f"{isodate.parse_duration(duration_iso)}"


def render_xml_feed(
    playlist_data: list[dict], channel_data: ChannelEntry, podcast_type: str
):
    # todo worth making class for?
    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist_data]

    videos_data = yt_videos(video_ids)

    for item in videos_data:
        _fix_datetimes(item)

    all_data = {
        "video_info": videos_data,
        "channel_data": channel_data,
        "podcast_type": podcast_type,
        "media_extension": "m4a" if podcast_type == "audio" else "mp4",
    }
    domain = os.getenv("DOMAIN")
    return render_template(
        "feed.xml.jinja", videos_data=all_data, DOMAIN=domain if domain else 'localhost'
    )
