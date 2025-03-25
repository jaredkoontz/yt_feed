from flask import Blueprint
from flask import make_response
from flask import Response
from googleapiclient.errors import HttpError

from yt_feed.routes.channel import output_formats
from yt_feed.utils.render_feed import render_xml_feed
from yt_feed.utils.youtube_api_call import yt_channels
from yt_feed.utils.youtube_api_call import yt_playlist

playlist_page = Blueprint("playlist_page", __name__)


def playlist(playlist_id: str, data_format: str) -> Response | str:
    try:
        playlist_data = yt_playlist(playlist_id)
    except HttpError as e:
        return make_response(f"Invalid playlist id {playlist_id}\n{e}", 400)

    if len(playlist_data) == 0:
        return make_response(f"Empty playlist {playlist_id}", 400)

    # todo worth creating a class for?
    channel_id = playlist_data[0]["snippet"]["channelId"]

    channel_data = yt_channels(channel_id, user_id=True)
    return render_xml_feed(playlist_data, channel_data, data_format)


for suffix, format_type in output_formats.items():
    playlist_page.route("/p/<playlist_id>", defaults={"data_format": format_type})(
        playlist
    )
    playlist_page.route(
        "/playlist/<playlist_id>/v", defaults={"data_format": format_type}
    )(playlist)
