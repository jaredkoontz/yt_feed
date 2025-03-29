import datetime

from flask import render_template

from yt_feed.models.data_entries import ChannelEntry
from yt_feed.utils.batch_helper import batch_iter
from yt_feed.utils.env_vars import domain
from yt_feed.utils.youtube_api_call import yt_videos


def render_rss_feed(
    playlist_data: list[dict], channel_data: ChannelEntry, podcast_type: str
):
    videos_data = []
    for yt_id_batch in batch_iter(playlist_data):
        videos_data.extend(yt_videos(yt_id_batch))

    all_data = {
        "video_info": videos_data,
        "channel_data": channel_data,
        "podcast_type": podcast_type,
        "media_extension": "m4a" if podcast_type == "audio" else "mp4",
    }
    return render_template(
        "rss_feed.xml.jinja",
        now=datetime.datetime.now(datetime.UTC),
        videos_data=all_data,
        DOMAIN=domain(),
    )
