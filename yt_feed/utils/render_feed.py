import datetime
from email.utils import format_datetime

from flask import make_response
from flask import render_template

from yt_feed.models.data_entries import ChannelEntry
from yt_feed.utils.batch_helper import batch_iter
from yt_feed.utils.env_vars import domain
from yt_feed.utils.yt_api_wrapper import yt_videos


def render_rss_feed(playlist_data: list[dict], channel_data: ChannelEntry):
    videos_data = []
    for yt_id_batch in batch_iter(playlist_data):
        videos_data.extend(yt_videos(yt_id_batch))

    all_data = {
        "video_info": videos_data,
        "channel_data": channel_data,
    }
    rss_xml = render_template(
        "rss_feed.xml.jinja",
        now=format_datetime(datetime.datetime.now(datetime.UTC), usegmt=True),
        videos_data=all_data,
        DOMAIN=domain(),
    )
    response = make_response(rss_xml)
    response.headers["Content-Type"] = "application/xml; charset=utf-8"
    return response
