import datetime

from flask import render_template

from yt_feed.models.channel_entry import ChannelEntry
from yt_feed.utils.env_vars import domain
from yt_feed.utils.youtube_api_call import yt_videos


def render_xml_feed(
    playlist_data: list[dict], channel_data: ChannelEntry, podcast_type: str
):
    # todo worth making class for?
    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist_data]

    videos_data = yt_videos(video_ids)

    all_data = {
        "video_info": videos_data,
        "channel_data": channel_data,
        "podcast_type": podcast_type,
        "media_extension": "m4a" if podcast_type == "audio" else "mp4",
    }
    return render_template(
        "feed.xml.jinja",
        now=datetime.datetime.now(datetime.UTC),
        videos_data=all_data,
        DOMAIN=domain(),
    )
