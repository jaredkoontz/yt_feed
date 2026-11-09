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
download_lock = FileLock(r"/tmp/download_route.lock")

# Protocols where the url is a single file a podcatcher can fetch in one go.
_SINGLE_FILE_PROTOCOLS = frozenset({"http", "https"})

# Live streams, and streams that ended but YouTube hasn't finished processing, take
# a while to become a normal video. Ask clients to back off for about that long.
_NOT_READY_RETRY_AFTER = 3600


def _is_single_file(result: dict) -> bool:
    """
    Live and just-ended streams are only offered as segmented formats (DASH or HLS).
    Their url points at one ~5 second fragment, so redirecting to it hands the client
    a "complete" download of a few seconds.
    """
    protocol = result.get("protocol")
    # an extraction that doesn't report a protocol is treated as a plain file
    return protocol is None or protocol in _SINGLE_FILE_PROTOCOLS


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
        # so we have to do string parsing to find out the error.
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
    if not _is_single_file(result):
        # deliberately not cached: once YouTube finishes processing the stream, a
        # retry should pick up the real single file format
        response = make_response(
            "This video is a live stream that YouTube has not finished processing, retry later",
            503,
        )
        response.headers["Retry-After"] = str(_NOT_READY_RETRY_AFTER)
        return response
    cache_audio_url(video_id, result["url"])
    return redirect(result["url"])
