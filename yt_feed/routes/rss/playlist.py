from flask import Blueprint
from flask import make_response
from flask import Response
from googleapiclient.errors import HttpError

from yt_feed.models.data_entries import ChannelEntry
from yt_feed.models.data_entries import parse_playlist_info
from yt_feed.utils.channel_cache import flask_cache
from yt_feed.utils.channel_cache import only_200
from yt_feed.utils.render_feed import render_rss_feed
from yt_feed.utils.yt_api_wrapper import yt_playlist_info
from yt_feed.utils.yt_api_wrapper import yt_videos_in_playlist

playlist_page = Blueprint("playlist_page", __name__)


@playlist_page.route("/p/<playlist_id>")
@flask_cache.cached(response_filter=only_200)
def playlist(playlist_id: str) -> Response | str:
    try:
        playlist_info = yt_playlist_info(playlist_id)
    except HttpError as e:
        return make_response(f"Invalid playlist id {playlist_id}\n{e}", 400)

    playlist_data = yt_videos_in_playlist(playlist_id)

    if len(playlist_data) == 0:
        return make_response(f"Empty playlist {playlist_id}", 400)

    channel_data = ChannelEntry.construct(
        parse_playlist_info(playlist_info[0]),
        f"https://www.youtube.com/playlist?list={playlist_id}",
    )
    return render_rss_feed(playlist_data, channel_data)
