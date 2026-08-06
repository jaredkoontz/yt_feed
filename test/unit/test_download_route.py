from contextlib import contextmanager

import pytest
from filelock import Timeout
from yt_dlp.utils import DownloadError

from yt_feed.routes import download
from yt_feed.utils.channel_cache import flask_cache
from yt_feed.utils.download_cache import cache_audio_url


class _FakeLock:
    @contextmanager
    def acquire(self, timeout: int):
        yield


class _TimeoutLock:
    def acquire(self, timeout: int):
        raise Timeout("busy")


class _RacingLock:
    """
    Mimics another request resolving the same video while we wait on the lock.
    """

    def __init__(self, video_id: str, url: str):
        self._video_id = video_id
        self._url = url

    @contextmanager
    def acquire(self, timeout: int):
        cache_audio_url(self._video_id, self._url)
        yield


class _CountingExtractor:
    """
    Stands in for extract_audio and records how often it actually ran.
    """

    def __init__(self, result: dict):
        self._result = result
        self.calls = 0

    def __call__(self, video_id: str) -> dict:
        self.calls += 1
        return self._result


@pytest.fixture(autouse=True)
def fake_lock(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(download, "download_lock", _FakeLock())


@pytest.fixture(autouse=True)
def clear_url_cache(app):
    # the cache lives on the app, which is a module level singleton, so entries
    # would otherwise leak between tests
    with app.app_context():
        flask_cache.clear()
    yield


def test_download_redirects_to_extracted_audio(client, monkeypatch):
    monkeypatch.setattr(
        download, "extract_audio", lambda video_id: {"url": "https://example.com/a.m4a"}
    )

    response = client.get("/dl/video123.m4a")

    assert response.status_code == 302
    assert response.headers["Location"] == "https://example.com/a.m4a"


def test_download_handles_missing_url(client, monkeypatch):
    monkeypatch.setattr(download, "extract_audio", lambda video_id: {})

    response = client.get("/dl/video123.m4a")

    assert response.status_code == 500
    assert response.get_data(as_text=True) == "Error downloading video"


def test_download_handles_age_restricted_video(client, monkeypatch):
    monkeypatch.setattr(
        download,
        "extract_audio",
        lambda video_id: (_ for _ in ()).throw(
            DownloadError("Sign in to confirm your age.")
        ),
    )

    response = client.get("/dl/video123.m4a")

    assert response.status_code == 501
    assert "age inappropriate" in response.get_data(as_text=True)


def test_download_handles_generic_download_error(client, monkeypatch):
    monkeypatch.setattr(
        download,
        "extract_audio",
        lambda video_id: (_ for _ in ()).throw(DownloadError("nope")),
    )

    response = client.get("/dl/video123.m4a")

    assert response.status_code == 500
    assert "Error downloading video: nope" in response.get_data(as_text=True)


def test_download_handles_busy_lock(client, monkeypatch):
    monkeypatch.setattr(download, "download_lock", _TimeoutLock())

    response = client.get("/dl/video123.m4a")

    assert response.status_code == 429
    assert response.get_data(as_text=True) == "Busy, retry shortly"


def test_download_reuses_a_resolved_url(client, monkeypatch):
    extractor = _CountingExtractor({"url": "https://example.com/a.m4a"})
    monkeypatch.setattr(download, "extract_audio", extractor)

    first = client.get("/dl/video123.m4a")
    second = client.get("/dl/video123.m4a")

    assert extractor.calls == 1
    assert first.headers["Location"] == second.headers["Location"]


def test_download_resolves_each_video_separately(client, monkeypatch):
    extractor = _CountingExtractor({"url": "https://example.com/a.m4a"})
    monkeypatch.setattr(download, "extract_audio", extractor)

    client.get("/dl/video123.m4a")
    client.get("/dl/video456.m4a")

    assert extractor.calls == 2


def test_download_serves_from_cache_while_the_lock_is_held(client, monkeypatch):
    extractor = _CountingExtractor({"url": "https://example.com/a.m4a"})
    monkeypatch.setattr(download, "extract_audio", extractor)
    client.get("/dl/video123.m4a")

    # a cached url should not wait on the lock at all
    monkeypatch.setattr(download, "download_lock", _TimeoutLock())
    response = client.get("/dl/video123.m4a")

    assert response.status_code == 302
    assert extractor.calls == 1


def test_download_uses_a_url_resolved_while_it_waited_for_the_lock(client, monkeypatch):
    extractor = _CountingExtractor({"url": "https://example.com/ours.m4a"})
    monkeypatch.setattr(download, "extract_audio", extractor)
    monkeypatch.setattr(
        download,
        "download_lock",
        _RacingLock("video123", "https://example.com/theirs.m4a"),
    )

    response = client.get("/dl/video123.m4a")

    assert response.headers["Location"] == "https://example.com/theirs.m4a"
    assert extractor.calls == 0


def test_download_does_not_cache_a_failed_extraction(client, monkeypatch):
    extractor = _CountingExtractor({})
    monkeypatch.setattr(download, "extract_audio", extractor)

    assert client.get("/dl/video123.m4a").status_code == 500
    assert client.get("/dl/video123.m4a").status_code == 500
    assert extractor.calls == 2


def test_download_does_not_cache_an_already_expired_url(client, monkeypatch):
    expired = "https://rr1.googlevideo.com/videoplayback?expire=1"
    extractor = _CountingExtractor({"url": expired})
    monkeypatch.setattr(download, "extract_audio", extractor)

    client.get("/dl/video123.m4a")
    second = client.get("/dl/video123.m4a")

    assert second.status_code == 302
    assert extractor.calls == 2
