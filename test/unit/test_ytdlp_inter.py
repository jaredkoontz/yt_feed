import pytest
import yt_dlp

from yt_feed.utils import ytdlp_inter


class _FakeYoutubeDL:
    """
    Stands in for yt_dlp.YoutubeDL and records how it was driven.
    """

    instances: list["_FakeYoutubeDL"] = []

    def __init__(self, ydl_opts, result=None, error=None):
        self.ydl_opts = ydl_opts
        self.result = result
        self.error = error
        self.exited = False
        self.extract_calls = []
        _FakeYoutubeDL.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.exited = True
        return False

    def extract_info(self, url, download):
        self.extract_calls.append((url, download))
        if self.error:
            raise self.error
        return self.result


@pytest.fixture
def fake_ytdl(monkeypatch: pytest.MonkeyPatch):
    _FakeYoutubeDL.instances.clear()

    def _install(result=None, error=None) -> None:
        monkeypatch.setattr(
            yt_dlp,
            "YoutubeDL",
            lambda ydl_opts: _FakeYoutubeDL(ydl_opts, result, error),
        )

    yield _install
    _FakeYoutubeDL.instances.clear()


def test_extract_audio_returns_the_info_dict(fake_ytdl):
    info = {"url": "https://example.com/a.m4a", "id": "video123"}
    fake_ytdl(result=info)

    assert ytdlp_inter.extract_audio("video123") == info


def test_extract_audio_never_downloads_the_video(fake_ytdl):
    fake_ytdl(result={"url": "https://example.com/a.m4a"})

    ytdlp_inter.extract_audio("video123")

    ydl = _FakeYoutubeDL.instances[0]
    assert ydl.extract_calls == [("video123", False)]


def test_extract_audio_asks_for_audio_only_formats(fake_ytdl):
    fake_ytdl(result={"url": "https://example.com/a.m4a"})

    ytdlp_inter.extract_audio("video123")

    assert _FakeYoutubeDL.instances[0].ydl_opts["format"] == "m4a/bestaudio/best"


def test_extract_audio_closes_the_downloader(fake_ytdl):
    fake_ytdl(result={"url": "https://example.com/a.m4a"})

    ytdlp_inter.extract_audio("video123")

    assert _FakeYoutubeDL.instances[0].exited


def test_extract_audio_closes_the_downloader_when_extraction_fails(fake_ytdl):
    fake_ytdl(error=yt_dlp.utils.DownloadError("nope"))

    with pytest.raises(yt_dlp.utils.DownloadError):
        ytdlp_inter.extract_audio("video123")

    assert _FakeYoutubeDL.instances[0].exited
