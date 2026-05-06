import os
from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def set_config(monkeypatch):
    with mock.patch.dict(os.environ, clear=True):
        envvars = {
            "DOMAIN ": "localhost",
            "YOUTUBE_API_KEY": "deadbeef",
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield
