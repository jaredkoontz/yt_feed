from flask import Blueprint
from flask import render_template
from flask import request
from flask import Response

from yt_feed.utils.env_vars import domain
from yt_feed.utils.feed_path import feed_path_for

index_page = Blueprint("index_page", __name__)


@index_page.route("/")
def home() -> Response | str:
    pasted = request.args.get("url", "").strip()
    feed_path = feed_path_for(pasted) if pasted else None
    return render_template(
        "index.html.jinja",
        DOMAIN=domain(),
        PASTED=pasted,
        FEED_URL=f"{domain()}{feed_path}" if feed_path else None,
    )
