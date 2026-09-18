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


class _PagingCollection:
    """
    Returns a canned sequence of api responses, one per list() call, and records
    the page token it was asked for each time.
    """

    def __init__(self, pages: list[dict]):
        self._pages = list(pages)
        self.page_tokens: list[str] = []

    def list(self, **kwargs):
        self.page_tokens.append(kwargs["pageToken"])
        return _FakeListRequest(self._pages.pop(0))


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


def test_youtube_builds_the_v3_service_with_the_configured_key(
    monkeypatch: pytest.MonkeyPatch,
):
    built = {}

    def _fake_build(service_name, version, developerKey):
        built.update(
            service_name=service_name, version=version, developerKey=developerKey
        )
        return _FakeYouTube()

    monkeypatch.setattr(yt_api_wrapper, "build", _fake_build)
    monkeypatch.setattr(
        yt_api_wrapper.env_vars, "youtube_api_key", lambda: "test-api-key"
    )

    assert isinstance(yt_api_wrapper._youtube(), _FakeYouTube)
    assert built == {
        "service_name": "youtube",
        "version": "v3",
        "developerKey": "test-api-key",
    }


def test_yt_channels_closes_youtube_service(monkeypatch: pytest.MonkeyPatch):
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
    assert service.closed


def test_paginated_calls_close_youtube_service(monkeypatch: pytest.MonkeyPatch):
    service = _FakeYouTube({"items": [{"id": "PL123"}]})
    _patch_youtube(monkeypatch, service)

    with yt_api_wrapper.youtube_service() as youtube:
        assert yt_api_wrapper.yt_playlist_info(youtube, "PL123") == [{"id": "PL123"}]
        assert not service.closed

    assert service.closed


def test_get_all_items_follows_every_page():
    collection = _PagingCollection(
        [
            {"items": [{"id": "a"}], "nextPageToken": "page-2"},
            {"items": [{"id": "b"}], "nextPageToken": "page-3"},
            {"items": [{"id": "c"}]},
        ]
    )

    items = yt_api_wrapper._get_all_items(lambda: collection, {"part": "snippet"})

    assert items == [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    assert collection.page_tokens == ["", "page-2", "page-3"]


def test_get_all_items_tolerates_a_page_without_items():
    collection = _PagingCollection(
        [
            {"nextPageToken": "page-2"},
            {"items": [{"id": "b"}]},
        ]
    )

    items = yt_api_wrapper._get_all_items(lambda: collection, {"part": "snippet"})

    assert items == [{"id": "b"}]


def test_youtube_service_closes_when_execute_raises(monkeypatch: pytest.MonkeyPatch):
    service = _FakeYouTube(error=RuntimeError("api failed"))
    _patch_youtube(monkeypatch, service)

    with pytest.raises(RuntimeError, match="api failed"):
        with yt_api_wrapper.youtube_service() as youtube:
            yt_api_wrapper.yt_playlist_info(youtube, "PL123")

    assert service.closed is True
