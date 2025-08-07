from flask import Flask

from yt_feed.routes.download import download_route
from yt_feed.routes.index import index_page
from yt_feed.routes.rss.channel import channel_page
from yt_feed.routes.rss.playlist import playlist_page
from yt_feed.routes.rss.yt_user import user_page
from yt_feed.utils.channel_cache import cache_config
from yt_feed.utils.channel_cache import flask_cache

yt_feed_app = Flask(__name__, template_folder="templates")

yt_feed_app.register_blueprint(channel_page)
yt_feed_app.register_blueprint(download_route)
yt_feed_app.register_blueprint(index_page)
yt_feed_app.register_blueprint(playlist_page)
yt_feed_app.register_blueprint(user_page)

flask_cache.init_app(yt_feed_app, cache_config)
