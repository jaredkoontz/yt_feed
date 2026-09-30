import pytest

from yt_feed.utils.feed_path import feed_path_for


@pytest.mark.parametrize(
    "raw, expected",
    [
        # the README examples
        ("https://www.youtube.com/c/CoryWongMusic", "/c/CoryWongMusic"),
        ("https://youtube.com/c/@AdamNeely", "/c/@AdamNeely"),
        (
            "https://www.youtube.com/playlist?list=PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt",
            "/p/PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt",
        ),
        (
            "https://www.youtube.com/channel/UCj1VqrHhDte54oLgPG4xpuQ",
            "/u/UCj1VqrHhDte54oLgPG4xpuQ",
        ),
        ("https://www.youtube.com/watch?v=5LyUgE4XPuU", "/dl/5LyUgE4XPuU.m4a"),
        # other url shapes
        ("https://www.youtube.com/@AdamNeely", "/c/@AdamNeely"),
        ("https://www.youtube.com/@AdamNeely/videos", "/c/@AdamNeely"),
        ("youtube.com/@AdamNeely", "/c/@AdamNeely"),
        ("  https://m.youtube.com/@AdamNeely  ", "/c/@AdamNeely"),
        (
            "https://www.youtube.com/channel/UCj1VqrHhDte54oLgPG4xpuQ/videos",
            "/u/UCj1VqrHhDte54oLgPG4xpuQ",
        ),
        (
            "https://www.youtube.com/watch?v=5LyUgE4XPuU&list=PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt",
            "/p/PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt",
        ),
        ("https://youtu.be/Xo3xqm-AtqE?t=10", "/dl/Xo3xqm-AtqE.m4a"),
        # bare handles and ids
        ("@AdamNeely", "/c/@AdamNeely"),
        ("UCj1VqrHhDte54oLgPG4xpuQ", "/u/UCj1VqrHhDte54oLgPG4xpuQ"),
        (
            "PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt",
            "/p/PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt",
        ),
    ],
)
def test_feed_path_for(raw, expected):
    assert feed_path_for(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "https://example.com/@AdamNeely",
        "https://www.youtube.com/",
        "https://www.youtube.com/watch",
        "https://www.youtube.com/watch?v=<script>",
        "https://www.youtube.com/channel/not-a-channel-id",
        "https://www.youtube.com/channel",
        "https://www.youtube.com/c",
        "https://www.youtube.com/c/<script>",
        "https://www.youtube.com/@",
        "https://www.youtube.com/feed/subscriptions",
        "https://youtu.be/",
        "https://youtu.be/<script>",
        "not a url",
    ],
)
def test_feed_path_for_rejects(raw):
    assert feed_path_for(raw) is None
