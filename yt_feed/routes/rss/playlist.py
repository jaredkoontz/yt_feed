from flask import Blueprint
from flask import Response

from yt_feed.routes.rss.endpoint_helpers import create_rss_from_playlist
from yt_feed.utils.channel_cache import flask_cache
from yt_feed.utils.channel_cache import only_200

playlist_page = Blueprint("playlist_page", __name__)


@playlist_page.route("/p/<playlist_id>")
@flask_cache.cached(response_filter=only_200)
def playlist(playlist_id: str) -> Response | str:
    return create_rss_from_playlist(playlist_id)
