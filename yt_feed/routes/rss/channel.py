from flask import Blueprint
from flask import Response

from yt_feed.routes.rss._make_xml_from_channel import _create_rss_from_channel
from yt_feed.utils.channel_cache import flask_cache
from yt_feed.utils.channel_cache import only_200

channel_page = Blueprint("channel_page", __name__)


@channel_page.route("/c/<yt_user>")
@flask_cache.cached(response_filter=only_200)
def channel(yt_user: str) -> Response | str:
    return _create_rss_from_channel(
        yt_user, False, f"https://www.youtube.com/c/{yt_user}"
    )
