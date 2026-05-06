import os
from unittest import mock

import pytest

from yt_feed.utils import yt_api_wrapper


class _FakeListRequest:
    def __init__(self, response: dict | None = None, error: Exception | None = None):
        self._response = response
        self._error = error

    def execute(self):
        if self._error:
            raise self._error
        return self._response


class _FakeCollection:
    def __init__(self, response: dict | None = None, error: Exception | None = None):
        self._response = response
        self._error = error

    def list(self, **kwargs):
        return _FakeListRequest(self._response, self._error)


class _FakeYouTube:
    def __init__(self, response: dict | None = None, error: Exception | None = None):
        self.closed = False
        self._response = response
        self._error = error

    def close(self):
        self.closed = True

    def channels(self):
        return _FakeCollection(self._response, self._error)

    def playlists(self):
        return _FakeCollection(self._response, self._error)


def _patch_youtube(monkeypatch: pytest.MonkeyPatch, service: _FakeYouTube) -> None:
    monkeypatch.setattr(yt_api_wrapper, "_youtube", lambda: service)


@pytest.fixture()
def set_config(monkeypatch):
    with mock.patch.dict(os.environ, clear=True):
        envvars = {
            "DOMAIN ": "localhost",
            "YOUTUBE_API_KEY": "deadbeef",
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield


def test_yt_channels_closes_youtube_service(
    set_config, monkeypatch: pytest.MonkeyPatch
):
    service = _FakeYouTube(
        {
            "items": [
                {
                    "snippet": {
                        "title": "Test Channel",
                        "description": "",
                        "thumbnails": {"high": {"url": "https://example.com/t.jpg"}},
                    },
                    "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}},
                }
            ]
        }
    )
    _patch_youtube(monkeypatch, service)

    with yt_api_wrapper.youtube_service() as youtube:
        channel = yt_api_wrapper.yt_channels(
            youtube, "UC123", True, "https://example.com/channel"
        )
        assert service.closed is False

    assert channel.title == "Test Channel"
    assert service.closed is True


def test_paginated_calls_close_youtube_service(
    set_config, monkeypatch: pytest.MonkeyPatch
):
    service = _FakeYouTube({"items": [{"id": "PL123"}]})
    _patch_youtube(monkeypatch, service)

    with yt_api_wrapper.youtube_service() as youtube:
        assert yt_api_wrapper.yt_playlist_info(youtube, "PL123") == [{"id": "PL123"}]
        assert service.closed is False

    assert service.closed is True


def test_youtube_service_closes_when_execute_raises(
    set_config, monkeypatch: pytest.MonkeyPatch
):
    service = _FakeYouTube(error=RuntimeError("api failed"))
    _patch_youtube(monkeypatch, service)

    with pytest.raises(RuntimeError, match="api failed"):
        with yt_api_wrapper.youtube_service() as youtube:
            yt_api_wrapper.yt_playlist_info(youtube, "PL123")

    assert service.closed is True
