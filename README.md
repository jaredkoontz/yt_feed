# yt_feed

Create a working RSS feed (for your podcatcher) to turn a YouTube channel into a podcast.

[![yt_feed](https://github.com/jaredkoontz/yt_feed/actions/workflows/python-app.yml/badge.svg)](https://github.com/jaredkoontz/yt_feed/actions/workflows/python-app.yml)
[![Docker](https://github.com/jaredkoontz/yt_feed/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/jaredkoontz/yt_feed/actions/workflows/docker-publish.yml)

## User Instructions

<ul>
    <li>
        <p>Works on any playlist or channel, get the handle or id from the url, and create a new url on
            this website. Examples:</p>
        <ul>
            Channel:
            <li><code><a href="https://youtube.com/c/@stuffmadehere">https://youtube.com/c/@stuffmadehere</a></code>
                <ol>
                    <li><code><a href="http://localhost:5446/c/@stuffmadehere">http://localhost:5446/c/@stuffmadehere</a></code></li>
                </ol>
            </li>
            <li><code><a href="https://youtube.com/c/beardmeatsfood">https://youtube.com/c/beardmeatsfood</a></code>
                <ol>
                    <li><code><a href="http://localhost:5446/c/beardmeatsfood">http://localhost:5446/c/beardmeatsfood</a></code></li>
                </ol>
            </li>
            Playlist:
            <li>
                <code><a href="https://www.youtube.com/watch?v=KMd5czoOW-Q&list=PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt">https://www.youtube.com/watch?v=KMd5czoOW-Q&list=PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt</a></code>
                <ol>
                    <li><code><a href="http://localhost:5446/p/PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt">http://localhost:5446/p/PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt</a></code>
                    </li>
                </ol>
            </li>
            <li>
                <code><a href="https://www.youtube.com/watch?v=jX4LEyTgZNQ&list=PLz4scdcuqnN2oK16dHadxF1JTAaW1snBu">https://www.youtube.com/watch?v=jX4LEyTgZNQ&list=PLz4scdcuqnN2oK16dHadxF1JTAaW1snBu</a></code>
                <ol>
                    <li>
                        <code><a href="http://localhost:5446/p/PLz4scdcuqnN2oK16dHadxF1JTAaW1snBu">http://localhost:5446/u/PLz4scdcuqnN2oK16dHadxF1JTAaW1snBu</a></code>
                    </li>
                </ol>
            </li>
            User:
            <li><code><a href="https://www.youtube.com/channel/UCj1VqrHhDte54oLgPG4xpuQ">https://www.youtube.com/channel/UCj1VqrHhDte54oLgPG4xpuQ</a></code>
                <ol>
                    <li>
                        <code><a href="http://localhost:5446/u/UCj1VqrHhDte54oLgPG4xpuQ">http://localhost:5446/u/UCj1VqrHhDte54oLgPG4xpuQ</a></code>
                    </li>
                </ol>
            </li>
        </ul>
    </li>

    <li>
        <p>Add this RSS feed to your podcatcher of choice and pretend that your favorite content creator created a
            podcast</p>
    </li>
    <li>
        <p>If you want to download a single video, you can use the `download` routes. Examples:</p>
        <ul>
            <li>
                <code><a href="https://www.youtube.com/watch?v=8kKwfZpbIv8">https://www.youtube.com/watch?v=8kKwfZpbIv8</a></code>
                <ol>
                    <li><code><a href="http://localhost:5446/dl/8kKwfZpbIv8.m4a">http://localhost:5446/dl/8kKwfZpbIv8.m4a</a></code>
                    </li>
                </ol>
            </li>
            <li>
                <code><a href="https://www.youtube.com/watch?v=Xo3xqm-AtqE">https://www.youtube.com/watch?v=Xo3xqm-AtqE</a></code>
                <ol>
                    <li><code><a href="http://localhost:5446/dl/Xo3xqm-AtqE.m4a">http://localhost:5446/dl/Xo3xqm-AtqE.m4a</a></code>
                    </li>
                </ol>
            </li>
        </ul>
    </li>
</ul>

## Hosting

### Pre-reqs

You'll need a YouTube api key.

### Docker

We publish a docker container that contains the latest code at `ghcr.io/jaredkoontz/yt_feed:main`.

```shell
docker run\
 -e YOUTUBE_API_KEY="your_key_here"\
 -e DOMAIN="your_domain_here"\
 -p 80:80\
 --rm -d\
 ghcr.io/jaredkoontz/yt_feed:main
```

Ensure it is running

`curl localhost`

### Local Run

Currently running on python:3.12

1. Install uv
2. sync envirornment
   `uv sync`
3. run flask app
   ` YOUTUBE_API_KEY=some_key DOMAIN=your_domain && uv run python wsgi.py`

Ensure it is running

`curl localhost:5446`
