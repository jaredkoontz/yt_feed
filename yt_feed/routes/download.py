from flask import Blueprint
from flask import make_response
from flask import redirect
from flask import Response

from yt_feed.utils.ytdlp_inter import extract_audio
from yt_feed.utils.ytdlp_inter import extract_video

download_page = Blueprint("download_page", __name__)


@download_page.route("/dl/<media_type>/<video_id>.<suffix>")
def yt_dl(media_type: str, video_id: str, suffix: str) -> Response:
    if media_type == "video":
        result = extract_video(video_id)
        r = result["url"]

    elif media_type == "audio":
        result = extract_audio(video_id)
        r = result["url"]
    else:
        return make_response("Unsupported format", 400)

    return redirect(r)
