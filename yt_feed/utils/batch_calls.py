from itertools import islice

from yt_feed.models.data_entries import parse_video_id

_BATCH_SIZE = 50


def batch_yt_calls(playlist_data):
    """
    youtube uses GET for all of these calls, so we are bounded by the url limit.
    If we have a lot of video ids, we need to batch them, 50 at a time seems reasonable.
    """
    video_ids = [parse_video_id(video_id) for video_id in playlist_data]
    it = iter(video_ids)
    while batch := list(islice(it, _BATCH_SIZE)):
        yield batch
