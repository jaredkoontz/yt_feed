import pytest

from yt_feed.web_app import yt_feed_app


@pytest.fixture()
def app():
    app = yt_feed_app
    app.config.update({
        "TESTING": True,
    })

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()