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


_ref = _EnvVarHelper()


def domain() -> str:
    assert _ref is not None
    assert type(_ref.domain) is str
    return _ref.domain


def youtube_api_key() -> str:
    return _ref.yt_api_key
