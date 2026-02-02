import ssl

from flask import make_response
from googleapiclient.errors import HttpError

from yt_feed.models.data_entries import ChannelEntry
from yt_feed.models.data_entries import parse_playlist_info
from yt_feed.models.errors import BadChannelException
from yt_feed.utils.render_feed import render_rss_feed
from yt_feed.utils.yt_api_wrapper import yt_channels
from yt_feed.utils.yt_api_wrapper import yt_playlist_info
from yt_feed.utils.yt_api_wrapper import yt_videos_in_playlist


def _validate_and_render(channel_data, playlist_id):
    try:
        playlist_data = yt_videos_in_playlist(playlist_id)
    except (ssl.SSLError, AttributeError):
        return make_response(
            "Try again",
            503,
        )
    if len(playlist_data) == 0:
        return make_response(f"Empty playlist {playlist_id}", 400)
    return render_rss_feed(playlist_data, channel_data)


def create_rss_from_playlist(playlist_id: str):
    try:
        playlist_info = yt_playlist_info(playlist_id)
    except HttpError as e:
        return make_response(f"Invalid playlist id {playlist_id}\n{e}", 400)
    if not playlist_info:
        return make_response(f"Invalid playlist id {playlist_id}", 400)

    channel_data = ChannelEntry.construct(
        parse_playlist_info(playlist_info[0]),
        f"https://www.youtube.com/playlist?list={playlist_id}",
    )
    return _validate_and_render(channel_data, playlist_id)


def create_rss_from_channel(yt_user: str, request_type: bool, channel_url: str):
    """
    A channel and a user are essentially the same thing, but the YouTube api will either want an
    id or a handle.

    Let's treat them the same. This helper will get called on both the channel and user endpoints.
    """
    try:
        channel_data = yt_channels(yt_user, request_type, channel_url)
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
    return _validate_and_render(channel_data, channel_data.playlist_id)
