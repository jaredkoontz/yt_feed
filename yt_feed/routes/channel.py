from flask import Blueprint
from flask import Response

from yt_feed.routes._make_xml_from_channel import _create_rss_from_channel
from yt_feed.utils.channel_cache import flask_cache

channel_page = Blueprint("channel_page", __name__)


@channel_page.route("/c/<yt_user>", defaults={"data_format": "audio"})
@channel_page.route("/c/<yt_user>/v", defaults={"data_format": "video"})
@flask_cache.cached()
def channel(yt_user: str, data_format: str) -> Response | str:
    return _create_rss_from_channel(yt_user, data_format, False)
