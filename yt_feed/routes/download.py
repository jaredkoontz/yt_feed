from filelock import FileLock
from filelock import Timeout
from flask import Blueprint
from flask import make_response
from flask import redirect
from werkzeug import Response
from yt_dlp.utils import DownloadError

from yt_feed.utils.download_cache import cache_audio_url
from yt_feed.utils.download_cache import cached_audio_url
from yt_feed.utils.ytdlp_inter import extract_audio

download_route = Blueprint("download_page", __name__)
download_lock = FileLock("/tmp/download_route.lock")


@download_route.route("/dl/<video_id>.<suffix>")
def yt_dl(video_id: str, suffix: str) -> Response:
    known_url = cached_audio_url(video_id)
    if known_url:
        return redirect(known_url)
    try:
        # getting the url is memory expensive. we should try to limit the number of
        # processes that are downloading at once
        with download_lock.acquire(timeout=10):
            # whoever just held the lock may have resolved this very video, so a
            # burst of requests for one video costs a single extraction
            known_url = cached_audio_url(video_id)
            if known_url:
                return redirect(known_url)
            result = extract_audio(video_id)
    except DownloadError as e:
        # unfortunately, yt_dlp does not provide a way to get the error type. It is just a generic DownloadError
        # so we have to do string parsing.
        err_msg = e.msg
        if err_msg and "Sign in to confirm your age." in err_msg:
            return make_response(
                "Youtube has flagged this as age inappropriate content and we do not support cookies",
                501,
            )
        else:
            return make_response(f"Error downloading video: {err_msg}", 500)

    except Timeout:
        return make_response("Busy, retry shortly", 429)
    if not result.get("url"):
        return make_response("Error downloading video", 500)
    cache_audio_url(video_id, result["url"])
    return redirect(result["url"])
