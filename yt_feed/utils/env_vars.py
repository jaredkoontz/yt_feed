import os

from dotenv import load_dotenv

from yt_feed.models.errors import InvalidConfigException


class _EnvVarHelper:
    """
    Simple singleton around the instance since we only ever need to load this once.
    """

    def __init__(self):
        load_dotenv()
        self.__domain = os.getenv("DOMAIN")
        self.__yt_api = os.getenv("YOUTUBE_API_KEY")
        if not self.__domain or not self.__yt_api:
            raise InvalidConfigException(self.__domain, self.__yt_api)
        assert self.__yt_api is not None

    @property
    def domain(self):
        return self.__domain

    @property
    def yt_api_key(self):
        return self.__yt_api


_ref: _EnvVarHelper | None = None


def _env() -> _EnvVarHelper:
    global _ref
    if _ref is None:
        _ref = _EnvVarHelper()
    return _ref


def domain() -> str:
    value = _env().domain
    assert type(value) is str and value is not None
    return value


def youtube_api_key() -> str:
    value = _env().yt_api_key
    assert type(value) is str and value is not None
    return value
