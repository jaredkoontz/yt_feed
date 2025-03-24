import ssl

from flask import Blueprint
from flask import make_response
from flask import Response

from yt_feed.models.errors import BadChannelException
from yt_feed.utils.render_feed import render_xml_feed
from yt_feed.utils.youtube_api_call import yt_channels
from yt_feed.utils.youtube_api_call import yt_playlist

channel_page = Blueprint("channel_page", __name__)


def channel(id_type: str, yt_user: str, data_format: str) -> Response | str:
    try:
        channel_data = yt_channels(
            yt_user, user_id=(id_type == "u" or id_type == "user")
        )
    except (IndexError, BadChannelException):
        correct_path_choice = (
            "user" if id_type == "u" else "channel" if id_type == "c" else id_type
        )
        return make_response(
            # now that is a ternary
            f"It appears that {yt_user} is not a valid {correct_path_choice}.",
            404,
        )

    try:
        playlist_data = yt_playlist(channel_data.uploads)
    except ssl.SSLError:
        return make_response(
            "Try again",
            500,
        )
    return render_xml_feed(playlist_data, channel_data, data_format)


user_routes = [("c", "channel"), ("u", "user")]
output_formats = {
    "": "audio",
    # "/v": "video"
}
for short, full in user_routes:
    for suffix, format_type in output_formats.items():
        channel_page.route(
            f"/{short}/<yt_user>{suffix}",
            defaults={"id_type": full, "data_format": format_type},
        )(channel)
        channel_page.route(
            f"/{full}/<yt_user>{suffix}",
            defaults={"id_type": full, "data_format": format_type},
        )(channel)
