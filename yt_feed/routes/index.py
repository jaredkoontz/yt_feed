from flask import Blueprint
from flask import render_template
from flask import Response

from yt_feed.utils.env_vars import domain

index_page = Blueprint("index_page", __name__)


@index_page.route("/")
def home() -> Response | str:
    return render_template("index.html.jinja", DOMAIN=domain())
