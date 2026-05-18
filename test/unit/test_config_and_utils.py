import importlib

import pytest

from yt_feed.models.errors import InvalidConfigException
from yt_feed.utils import channel_cache
from yt_feed.utils import env_vars
from yt_feed.utils.batch_helper import batch_iter


def test_gunicorn_config_imports_expected_values():
    config = importlib.import_module("yt_feed.conf.gunicorn_conf")

    assert config.loglevel == "info"
    assert config.workers == 2
    assert config.timeout == 900


def test_only_200_filters_by_status_code():
    class _Response:
        def __init__(self, status_code: int):
            self.status_code = status_code

    # pyrefly: ignore [bad-argument-type]
    assert channel_cache.only_200(_Response(200))
    # pyrefly: ignore [bad-argument-type]
    assert not channel_cache.only_200(_Response(500))


def test_batch_iter_batches_video_ids():
    playlist_data = [
        {"snippet": {"resourceId": {"videoId": f"video-{i}"}}} for i in range(51)
    ]

    assert list(batch_iter(playlist_data)) == [
        tuple(f"video-{i}" for i in range(50)),
        ("video-50",),
    ]


def test_env_vars_raise_when_missing_required_values(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(env_vars, "_ref", None)
    monkeypatch.delenv("DOMAIN", raising=False)
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    monkeypatch.setattr(env_vars, "load_dotenv", lambda: None)

    with pytest.raises(InvalidConfigException) as exc_info:
        env_vars._env()

    assert "DOMAIN not set" in str(exc_info.value)
    assert "YOUTUBE_API_KEY not set" in str(exc_info.value)


def test_env_vars_cache_loaded_values(monkeypatch: pytest.MonkeyPatch):
    domain = "https://example.com"
    key = "deadbeef"
    monkeypatch.setattr(env_vars, "_ref", None)
    monkeypatch.setenv("DOMAIN", domain)
    monkeypatch.setenv("YOUTUBE_API_KEY", key)
    monkeypatch.setattr(env_vars, "load_dotenv", lambda: None)

    assert env_vars.domain() == domain
    assert env_vars.youtube_api_key() == key
