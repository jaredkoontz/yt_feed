from typing import Callable

from googleapiclient.discovery import build

from yt_feed.models.data_entries import ChannelEntry
from yt_feed.models.data_entries import make_channel_entry
from yt_feed.models.data_entries import make_video_entry
from yt_feed.models.data_entries import VideoEntry
from yt_feed.utils import env_vars

_RESULT_SIZE = 50
_WANTED_PART = "contentDetails,snippet"
_YOUTUBE = None


class _YT_Singleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if _YT_Singleton._instance is not None:
            raise RuntimeError("Use get_instance() to access the singleton instance")

        self.youtube = build("youtube", "v3", developerKey=env_vars.youtube_api_key())


def _youtube():
    return _YT_Singleton.get_instance().youtube


def _get_all_items(func: Callable, opts: dict[str, str]) -> list[dict]:
    """
    Handles the pagination from the api
    """

    data = []
    page_token = ""
    while True:
        res = (
            func()
            .list(
                **opts,
                maxResults=_RESULT_SIZE,
                pageToken=page_token,
            )
            .execute()
        )
        v = res.get("items", [])
        if v:
            data.extend(v)
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return data


def yt_channels(username_or_id: str, user_id: bool) -> ChannelEntry:
    if user_id:
        opts = {"id": username_or_id}
    else:
        opts = {"forHandle": username_or_id}

    # we are not paginating here
    request = (
        _youtube().channels().list(**opts, part=_WANTED_PART, maxResults=_RESULT_SIZE)
    )
    return make_channel_entry(request.execute())


def yt_playlist(playlist_id: str) -> list[dict]:
    opts = {"playlistId": playlist_id, "part": _WANTED_PART}
    return _get_all_items(_youtube().playlistItems, opts)


def yt_videos(video_ids: list[str]) -> list[VideoEntry]:
    all_videos = _get_all_items(
        _youtube().videos,
        {"id": ",".join(video_ids), "part": _WANTED_PART},
    )
    assert len(all_videos) == len(video_ids)
    return [make_video_entry(x) for x in all_videos]
