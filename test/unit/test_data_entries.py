import datetime

import pytest

from test.data.channel_data import channel
from test.data.video_data import video_data
from yt_feed.models.data_entries import ChannelEntry
from yt_feed.models.data_entries import parse_video_id
from yt_feed.models.data_entries import VideoEntry
from yt_feed.models.errors import BadChannelException


def test_channel_entry_allows_missing_uploads_playlist():
    raw = {
        "items": [
            {
                "snippet": {
                    "title": "A <channel>",
                    "description": "A description",
                    "thumbnails": {"high": {"url": "https://example.com/thumb.jpg"}},
                },
                "contentDetails": {"relatedPlaylists": {}},
            }
        ]
    }

    entry = ChannelEntry.construct(raw, "https://example.com/channel")

    assert entry.title == "A &lt;channel&gt;"
    assert entry.playlist_id == ""


def test_channel_entry_constructs_from_manual_playlist_info():
    entry = ChannelEntry.construct(
        {
            "title": "Playlist title",
            "description": "Playlist description",
            "thumbnail_url": "https://example.com/playlist.jpg",
        },
        "https://example.com/playlist",
    )

    assert entry == ChannelEntry(
        title="Playlist title",
        desc="Playlist description",
        thumbnail_url="https://example.com/playlist.jpg",
        originating_url="https://example.com/playlist",
        playlist_id="",
    )


def test_channel_entry_rejects_missing_required_manual_data():
    with pytest.raises(BadChannelException):
        ChannelEntry.construct({"title": "No thumbnail"}, "https://example.com")


def test_video_entry_rejects_missing_data():
    assert VideoEntry.construct({"id": "missing-snippet"}) is None


def test_video_entry_rejects_short_duration():
    raw = video_data[0] | {"contentDetails": {"duration": "PT5S"}}

    assert VideoEntry.construct(raw) is None


def test_video_entry_constructs_duration_as_timedelta():
    entry = VideoEntry.construct(video_data[0])

    assert entry is not None
    assert isinstance(entry.duration, datetime.timedelta)


def test_parse_video_id():
    assert (
        parse_video_id({"snippet": {"resourceId": {"videoId": "abc123"}}}) == "abc123"
    )


def test_channel_fixture_still_constructs():
    assert ChannelEntry.construct(channel, "https://example.com").playlist_id
