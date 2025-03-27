from flask import Flask

from yt_feed.routes.channel import channel_page
from yt_feed.routes.download import download_page
from yt_feed.routes.index import index_page
from yt_feed.routes.playlist import playlist_page
from yt_feed.routes.yt_user import user_page

app = Flask(__name__, template_folder="templates")

app.register_blueprint(channel_page)
app.register_blueprint(download_page)
app.register_blueprint(index_page)
app.register_blueprint(playlist_page)
app.register_blueprint(user_page)
