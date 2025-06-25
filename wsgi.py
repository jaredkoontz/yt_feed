from yt_feed.web_app import yt_feed_app

"""
For local dev only. For prod you should be using gunicorn
"""

if __name__ == "__main__":
    yt_feed_app.run(host="0.0.0.0", port=5446)
