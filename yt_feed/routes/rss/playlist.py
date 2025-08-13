from flask import Blueprint
from flask import make_response
from flask import Response
from googleapiclient.errors import HttpError

from yt_feed.models.data_entries import parse_channel_id
from yt_feed.utils.channel_cache import flask_cache
from yt_feed.utils.render_feed import render_rss_feed
from yt_feed.utils.yt_api_wrapper import yt_channels
from yt_feed.utils.yt_api_wrapper import yt_playlist

playlist_page = Blueprint("playlist_page", __name__)


@playlist_page.route("/p/<playlist_id>")
@flask_cache.cached()
def playlist(playlist_id: str) -> Response | str:
    try:
        playlist_data = yt_playlist(playlist_id)
    except HttpError as e:
        return make_response(f"Invalid playlist id {playlist_id}\n{e}", 400)

    if len(playlist_data) == 0:
        return make_response(f"Empty playlist {playlist_id}", 400)

    channel_id = parse_channel_id(playlist_data)

    channel_data = yt_channels(
        channel_id, True, f"https://www.youtube.com/playlist?list={playlist_id}"
    )
    return render_rss_feed(playlist_data, channel_data)
