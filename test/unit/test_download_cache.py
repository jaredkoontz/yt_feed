from yt_feed.utils.download_cache import cache_timeout

_NOW = 1_700_000_000.0


def _url_expiring_at(expiry: int | str) -> str:
    return f"https://rr1.googlevideo.com/videoplayback?expire={expiry}&itag=140"


def test_timeout_falls_back_when_url_has_no_expiry():
    assert cache_timeout("https://example.com/a.m4a", now=_NOW) == 3600


def test_timeout_falls_back_when_expiry_is_not_a_number():
    assert cache_timeout(_url_expiring_at("soon"), now=_NOW) == 3600


def test_timeout_falls_back_for_a_malformed_url():
    assert cache_timeout("https://[not-a-real-host", now=_NOW) == 3600


def test_timeout_leaves_a_margin_before_the_url_expires():
    one_hour_out = int(_NOW) + 3600

    # the full hour, less the 15 minute safety margin
    assert cache_timeout(_url_expiring_at(one_hour_out), now=_NOW) == 2700


def test_timeout_is_capped_for_absurdly_distant_expiries():
    a_year_out = int(_NOW) + 365 * 24 * 3600

    assert cache_timeout(_url_expiring_at(a_year_out), now=_NOW) == 21600


def test_timeout_is_zero_for_an_already_expired_url():
    an_hour_ago = int(_NOW) - 3600

    assert cache_timeout(_url_expiring_at(an_hour_ago), now=_NOW) == 0


def test_timeout_is_zero_inside_the_safety_margin():
    barely_alive = int(_NOW) + 60

    assert cache_timeout(_url_expiring_at(barely_alive), now=_NOW) == 0
