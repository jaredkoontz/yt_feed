import os

import pytest


@pytest.fixture()
def app(monkeypatch):
    envs = {
        "DOMAIN": "http://0.0.0.0",
        "YOUTUBE_API_KEY": "deadbeef",
    }
    monkeypatch.setattr(os, "environ", envs)

    from yt_feed.web_app import yt_feed_app

    app = yt_feed_app
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
