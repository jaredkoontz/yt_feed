from flask import Blueprint
from flask import Response

from yt_feed.routes._make_xml_from_channel import _create_rss_from_channel

user_page = Blueprint("user_page", __name__)


@user_page.route("/u/<yt_user>", defaults={"data_format": "audio"})
@user_page.route("/u/<yt_user>/v", defaults={"data_format": "video"})
def channel(yt_user: str, data_format: str) -> Response | str:
    return _create_rss_from_channel(yt_user, data_format, True)
