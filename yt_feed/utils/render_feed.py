from email.utils import parsedate_to_datetime

from flask import make_response
from flask import render_template
from flask import request
from flask import Response
from googleapiclient.discovery import Resource

from yt_feed.models.data_entries import ChannelEntry
from yt_feed.models.data_entries import VideoEntry
from yt_feed.utils.batch_helper import batch_iter
from yt_feed.utils.env_vars import domain
from yt_feed.utils.yt_api_wrapper import yt_videos_info


def _last_published(videos: list[VideoEntry]) -> str | None:
    """
    The feed's own dates follow its newest item rather than the clock, so rebuilding
    an unchanged feed produces identical bytes. Playlists are not ordered by date,
    so look at every item instead of trusting the first.
    """
    if not videos:
        return None
    return max(
        (v.published_at for v in videos),
        key=parsedate_to_datetime,
    )


def render_rss_feed(
    youtube: Resource, playlist_data: list[dict], channel_data: ChannelEntry
) -> Response:
    videos_data = []
    for yt_id_batch in batch_iter(playlist_data):
        videos_data.extend(yt_videos_info(youtube, yt_id_batch))

    all_data = {
        "video_info": videos_data,
        "channel_data": channel_data,
    }
    rss_xml = render_template(
        "rss_feed.xml.jinja",
        last_published=_last_published(videos_data),
        feed_url=f"{domain()}{request.path}",
        videos_data=all_data,
        DOMAIN=domain(),
    )
    response = make_response(rss_xml)
    response.headers["Content-Type"] = "application/xml; charset=utf-8"
    return response
