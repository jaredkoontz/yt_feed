from flask import Blueprint
from flask import make_response
from flask import Response
from googleapiclient.errors import HttpError

from yt_feed.models.data_entries import parse_channel_id
from yt_feed.utils.render_feed import render_rss_feed
from yt_feed.utils.youtube_api_call import yt_channels
from yt_feed.utils.youtube_api_call import yt_playlist

playlist_page = Blueprint("playlist_page", __name__)


@playlist_page.route("/p/<playlist_id>", defaults={"data_format": "audio"})
@playlist_page.route("/p/<playlist_id>/v", defaults={"data_format": "video"})
def playlist(playlist_id: str, data_format: str) -> Response | str:
    try:
        playlist_data = yt_playlist(playlist_id)
    except HttpError as e:
        return make_response(f"Invalid playlist id {playlist_id}\n{e}", 400)

    if len(playlist_data) == 0:
        return make_response(f"Empty playlist {playlist_id}", 400)

    channel_id = parse_channel_id(playlist_data)

    channel_data = yt_channels(channel_id, user_id=True)
    return render_rss_feed(playlist_data, channel_data, data_format)
