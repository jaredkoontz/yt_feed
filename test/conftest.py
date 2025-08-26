import os

import pytest

from test.data import channel_data
from test.data.playlist_contents_data import playlist_contents_data
from test.data.playlist_info_data import playlist_info_data
from test.data.video_data import video_data


@pytest.fixture
def mock_yt_api(monkeypatch: pytest.MonkeyPatch):
    class _FakeListReq:
        def __init__(self, response: dict):
            self._response = response

        def execute(self):
            return self._response

    class _FakeChannels:
        def list(self, **kwargs):
            return _FakeListReq(channel_data.channel)

    class _FakeCollection:
        def __init__(self, items: list[dict]):
            self._items = items

        def list(self, **kwargs):
            return _FakeListReq({"items": self._items})

    class _FakeYouTube:
        def channels(self):
            return _FakeChannels()

        def playlistItems(self):
            return _FakeCollection(playlist_contents_data)

        def playlists(self):
            return _FakeCollection(playlist_info_data)

        def videos(self):
            return _FakeCollection(video_data)

    monkeypatch.setattr(
        "yt_feed.utils.yt_api_wrapper._youtube",
        lambda: _FakeYouTube(),
        raising=True,
    )

    def _fake_get_all_items(func, opts):
        return func().list(**opts).execute()["items"]

    monkeypatch.setattr(
        "yt_feed.utils.yt_api_wrapper._get_all_items",
        _fake_get_all_items,
        raising=True,
    )
    return None


@pytest.fixture()
def app(monkeypatch):
    envs = {
        "DOMAIN": "http://0.0.0.0",
        "YOUTUBE_API_KEY": "deadbeef",
    }
    monkeypatch.setattr(os, "environ", envs)

    from yt_feed.web_app import yt_feed_app

    app = yt_feed_app
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
