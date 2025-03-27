import ssl

from flask import make_response

from yt_feed.models.errors import BadChannelException
from yt_feed.utils.render_feed import render_xml_feed
from yt_feed.utils.youtube_api_call import yt_channels
from yt_feed.utils.youtube_api_call import yt_playlist


def _create_from_channel(yt_user: str, data_format: str, request_type: bool):
    """
    A channel and a user are essentially the same thing, but the youtube api will either want am
    id or a handle. Thus, the error routes are handled the same way.
    """
    try:
        channel_data = yt_channels(yt_user, user_id=request_type)
    except (IndexError, BadChannelException):
        correct_path_choice = "user" if request_type else "channel"
        return make_response(
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
