from flask import Blueprint
from flask import make_response
from flask import redirect
from flask import Response

from yt_feed.utils.ytdlp_inter import extract_audio
from yt_feed.utils.ytdlp_inter import extract_video

download_page = Blueprint("download_page", __name__)


@download_page.route("/dl/<video_id>.<suffix>")
def yt_dl(video_id: str, suffix: str) -> Response:
    result = extract_audio(video_id)
    r = result["url"]
    return redirect(r)
