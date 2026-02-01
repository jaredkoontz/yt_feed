from filelock import FileLock
from filelock import Timeout
from flask import Blueprint
from flask import make_response
from flask import redirect
from flask import Response
from yt_dlp.utils import DownloadError

from yt_feed.utils.ytdlp_inter import extract_audio


download_route = Blueprint("download_page", __name__)
download_lock = FileLock("/tmp/download_route.lock")


@download_route.route("/dl/<video_id>.<suffix>")
def yt_dl(video_id: str, suffix: str) -> Response:
    try:
        # getting the url is memory expensive. we should try to limit the number of
        # processes that are downloading at once
        with download_lock.acquire(timeout=10):
            result = extract_audio(video_id)
    except DownloadError as e:
        # unfortunately, yt_dlp does not provide a way to get the error type. It is just a generic DownloadError
        # so we have to do string parsing.
        err_msg = e.msg
        if "Sign in to confirm your age." in err_msg:
            return make_response(
                "Youtube has flagged this as age inappropriate content and we do not support cookies",
                501,
            )
        else:
            return make_response(f"Error downloading video: {err_msg}", 500)

    except Timeout:
        return make_response("Busy, retry shortly", 429)

    return redirect(result["url"])
