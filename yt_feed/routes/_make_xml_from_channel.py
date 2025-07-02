import ssl

from flask import make_response

from yt_feed.models.errors import BadChannelException
from yt_feed.utils.render_feed import render_rss_feed
from yt_feed.utils.yt_api_wrapper import yt_channels
from yt_feed.utils.yt_api_wrapper import yt_playlist


def _create_rss_from_channel(yt_user: str, request_type: bool):
    """
    A channel and a user are essentially the same thing, but the YouTube api will either want an
    id or a handle.

    Let's treat them the same.
    """
    try:
        channel_data = yt_channels(yt_user, user_id=request_type)
    except (IndexError, BadChannelException):
        correct_path_choice = "user" if request_type else "channel"
        return make_response(
            f"It appears that {yt_user} is not a valid {correct_path_choice}.",
            404,
        )
    except ssl.SSLError:
        return make_response(
            "Try again",
            503,
        )
    try:
        playlist_data = yt_playlist(channel_data.uploads)
    except (ssl.SSLError, AttributeError):
        return make_response(
            "Try again",
            503,
        )
    return render_rss_feed(playlist_data, channel_data)
