import ssl

import pytest
from googleapiclient.errors import HttpError
from httplib2 import Response

from yt_feed.models.data_entries import ChannelEntry
from yt_feed.models.errors import BadChannelException
from yt_feed.routes.rss import endpoint_helpers


class _YoutubeContext:
    def __init__(self, youtube: object = object()):
        self.youtube = youtube

    def __enter__(self):
        return self.youtube

    def __exit__(self, exc_type, exc, traceback):
        return False


def _http_error() -> HttpError:
    return HttpError(Response({"status": "404", "reason": "bad"}), b"bad")


@pytest.fixture(autouse=True)
def patch_youtube_service(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(endpoint_helpers, "youtube_service", lambda: _YoutubeContext())


def test_validate_and_render_handles_transient_playlist_errors(app, monkeypatch):
    monkeypatch.setattr(
        endpoint_helpers,
        "yt_videos_in_playlist",
        lambda youtube, playlist_id: (_ for _ in ()).throw(ssl.SSLError("retry")),
    )

    with app.app_context():
        # pyrefly: ignore [bad-argument-type]
        response = endpoint_helpers._validate_and_render(object(), object(), "PL123")

    assert response.status_code == 503
    assert response.get_data(as_text=True) == "Try again"


def test_validate_and_render_rejects_empty_playlist(app, monkeypatch):
    monkeypatch.setattr(
        endpoint_helpers, "yt_videos_in_playlist", lambda youtube, playlist_id: []
    )

    with app.app_context():
        # pyrefly: ignore [bad-argument-type]
        response = endpoint_helpers._validate_and_render(object(), object(), "PL<bad>")

    assert response.status_code == 400
    assert "PL&lt;bad&gt;" in response.get_data(as_text=True)


def test_create_rss_from_playlist_handles_http_error(app, monkeypatch):
    monkeypatch.setattr(
        endpoint_helpers,
        "yt_playlist_info",
        lambda youtube, playlist_id: (_ for _ in ()).throw(_http_error()),
    )

    with app.app_context():
        response = endpoint_helpers.create_rss_from_playlist("PL<bad>")

    assert response.status_code == 400
    assert "Invalid playlist id PL&lt;bad&gt;" in response.get_data(as_text=True)


def test_create_rss_from_playlist_handles_empty_info(app, monkeypatch):
    monkeypatch.setattr(
        endpoint_helpers, "yt_playlist_info", lambda youtube, playlist_id: []
    )

    with app.app_context():
        response = endpoint_helpers.create_rss_from_playlist("PL123")

    assert response.status_code == 400


def test_create_rss_from_channel_handles_bad_channel(app, monkeypatch):
    monkeypatch.setattr(
        endpoint_helpers,
        "yt_channels",
        lambda youtube, user, request_type, url: (_ for _ in ()).throw(
            BadChannelException("bad", "")
        ),
    )

    with app.app_context():
        response = endpoint_helpers.create_rss_from_channel(
            "bad<user>", True, "https://example.com"
        )

    assert response.status_code == 404
    assert "bad&lt;user&gt;" in response.get_data(as_text=True)
    assert "valid user" in response.get_data(as_text=True)


def test_create_rss_from_channel_handles_ssl_error(app, monkeypatch):
    monkeypatch.setattr(
        endpoint_helpers,
        "yt_channels",
        lambda youtube, user, request_type, url: (_ for _ in ()).throw(
            ssl.SSLError("retry")
        ),
    )

    with app.app_context():
        response = endpoint_helpers.create_rss_from_channel(
            "bad-channel", False, "https://example.com"
        )

    assert response.status_code == 503


def test_create_rss_from_channel_renders_valid_channel(app, monkeypatch):
    channel = ChannelEntry(
        title="Title",
        desc="Desc",
        thumbnail_url="https://example.com/thumb.jpg",
        originating_url="https://example.com/channel",
        playlist_id="UU123",
    )
    monkeypatch.setattr(
        endpoint_helpers,
        "yt_channels",
        lambda youtube, user, request_type, url: channel,
    )
    monkeypatch.setattr(
        endpoint_helpers,
        "_validate_and_render",
        lambda youtube, channel_data, playlist_id: f"{channel_data.title}:{playlist_id}",
    )

    with app.app_context():
        response = endpoint_helpers.create_rss_from_channel(
            "good-channel", False, "https://example.com/channel"
        )

    assert response == "Title:UU123"
