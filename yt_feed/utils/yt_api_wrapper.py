from typing import Callable

from googleapiclient.discovery import build

from yt_feed.models.data_entries import ChannelEntry
from yt_feed.models.data_entries import VideoEntry
from yt_feed.utils import env_vars

_RESULT_SIZE = 50
_SNIPPET = "snippet"
_ALL_DETAILS = ",".join([_SNIPPET, "contentDetails"])


def _youtube():
    return build("youtube", "v3", developerKey=env_vars.youtube_api_key())


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


def yt_channels(username_or_id: str, is_id: bool, channel_url: str) -> ChannelEntry:
    opts = {"id": username_or_id} if is_id else {"forHandle": username_or_id}

    # we are not paginating here
    request = (
        _youtube().channels().list(**opts, part=_ALL_DETAILS, maxResults=_RESULT_SIZE)
    )
    return ChannelEntry.construct(request.execute(), channel_url)


def yt_videos_in_playlist(playlist_id: str) -> list[dict]:
    opts = {"playlistId": playlist_id, "part": _ALL_DETAILS}
    return _get_all_items(_youtube().playlistItems, opts)


def yt_playlist_info(playlist_id: str) -> list[dict]:
    opts = {"id": playlist_id, "part": _SNIPPET}
    return _get_all_items(_youtube().playlists, opts)


def yt_videos(video_ids: tuple[str, ...]) -> list[VideoEntry]:
    # todo do i need to be calling this in render rss feed? we might already have all the video ids that we want..
    all_videos = _get_all_items(
        _youtube().videos,
        {"id": ",".join(video_ids), "part": _ALL_DETAILS},
    )
    return [entry for x in all_videos if (entry := VideoEntry.construct(x)) is not None]
