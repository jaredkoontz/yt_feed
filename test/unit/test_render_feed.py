import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import pytest

from test.data.playlist_info_data import playlist_info_data
from yt_feed.utils.channel_cache import flask_cache

_ITUNES = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"
_ATOM = "{http://www.w3.org/2005/Atom}"


@pytest.fixture(autouse=True)
def clear_cache(app):
    # feed routes are cached by path, which would hide changes between tests
    with app.app_context():
        flask_cache.clear()


def _channel(client, path: str) -> ET.Element:
    response = client.get(path)
    assert response.status_code == 200
    # parsing is the real check: any unescaped text fails here
    channel = ET.fromstring(response.data).find("channel")
    assert channel is not None
    return channel


def test_feed_is_well_formed_xml(client, mock_yt_api):
    channel = _channel(client, "/c/foo")
    assert channel.findall("item")


def test_playlist_text_is_escaped(client, mock_yt_api, monkeypatch):
    snippet = playlist_info_data[0]["snippet"] | {
        "title": "Tips & Tricks <1>",
        "description": 'Say "hi" & <bye>',
    }
    monkeypatch.setattr(
        "yt_feed.routes.rss.endpoint_helpers.yt_playlist_info",
        lambda youtube, playlist_id: [playlist_info_data[0] | {"snippet": snippet}],
    )

    channel = _channel(client, "/p/foo")

    assert channel.findtext("title", "").startswith("Tips & Tricks <1> - ")
    assert channel.findtext("description") == 'Say "hi" & <bye>'


def test_video_text_is_not_double_escaped(client, mock_yt_api, monkeypatch):
    from test.data import video_data

    raw = video_data.video_data[0]
    patched = [raw | {"snippet": raw["snippet"] | {"title": "Q&A <live>"}}]
    # the fake videos() endpoint reads this name at call time
    monkeypatch.setattr("test.conftest.video_data", patched)

    channel = _channel(client, "/c/foo")

    assert channel.findtext("item/title") == "Q&A <live>"


def test_feed_with_every_video_filtered_is_still_valid(
    client, mock_yt_api, monkeypatch
):
    monkeypatch.setattr(
        "yt_feed.utils.render_feed.yt_videos_info", lambda youtube, ids: []
    )

    channel = _channel(client, "/c/foo")

    assert channel.findall("item") == []
    assert channel.find("lastBuildDate") is None


def test_self_link_points_at_the_feed(client, mock_yt_api):
    channel = _channel(client, "/c/foo")

    link = channel.find(f"{_ATOM}link")
    assert link is not None
    assert link.get("href") == "http://0.0.0.0/c/foo"


def test_feed_has_no_placeholder_contact_fields(client, mock_yt_api):
    channel = _channel(client, "/c/foo")

    assert channel.find("managingEditor") is None
    assert channel.find("webMaster") is None
    assert channel.find(f"{_ITUNES}owner/{_ITUNES}email") is None
    # item level <author> must be an email in RSS 2.0
    assert channel.find("item/author") is None


def test_feed_category_is_an_apple_category(client, mock_yt_api):
    category = _channel(client, "/c/foo").find(f"{_ITUNES}category")
    assert category is not None
    assert category.get("text") == "TV & Film"


def test_items_carry_enclosure_length_and_numeric_duration(client, mock_yt_api):
    for item in _channel(client, "/c/foo").findall("item"):
        enclosure = item.find("enclosure")
        assert enclosure is not None
        assert enclosure.get("length") == "0"
        assert item.findtext(f"{_ITUNES}duration", "").isdigit()


def test_duration_over_24_hours_is_whole_seconds(client, mock_yt_api, monkeypatch):
    from test.data import video_data

    raw = video_data.video_data[0]
    patched = [raw | {"contentDetails": raw["contentDetails"] | {"duration": "P1DT5S"}}]
    monkeypatch.setattr("test.conftest.video_data", patched)

    channel = _channel(client, "/c/foo")

    assert channel.findtext(f"item/{_ITUNES}duration") == "86405"


def test_feed_dates_follow_newest_item(client, mock_yt_api):
    channel = _channel(client, "/c/foo")

    newest = max(
        parsedate_to_datetime(item.findtext("pubDate", ""))
        for item in channel.findall("item")
    )
    assert parsedate_to_datetime(channel.findtext("lastBuildDate", "")) == newest
    assert channel.findtext("pubDate") == channel.findtext("lastBuildDate")


def test_rebuilding_an_unchanged_feed_is_byte_identical(app, client, mock_yt_api):
    first = client.get("/c/foo").data
    with app.app_context():
        flask_cache.clear()
    second = client.get("/c/foo").data

    assert first == second
