from contextlib import contextmanager

import pytest
from filelock import Timeout
from yt_dlp.utils import DownloadError

from yt_feed.routes import download


class _FakeLock:
    @contextmanager
    def acquire(self, timeout: int):
        yield


class _TimeoutLock:
    def acquire(self, timeout: int):
        raise Timeout("busy")


@pytest.fixture(autouse=True)
def fake_lock(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(download, "download_lock", _FakeLock())


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
