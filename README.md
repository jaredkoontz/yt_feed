# yt_feed


Create a working RSS feed (for your podcatcher) to turn a YouTube channel into a podcast.

[![yt_feed](https://github.com/jaredkoontz/yt_feed/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/jaredkoontz/yt_feed/actions/workflows/python-app.yml)
[![Docker](https://github.com/jaredkoontz/yt_feed/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/jaredkoontz/yt_feed/actions/workflows/docker-publish.yml)

## User Instructions

<ul>
    <li>
        <p>Works on any accessible playlist or channel, get the id from the url, and create a url using that id on this
            website.</p>
        <h4>Examples:</h4>
        <ul>
            Channel (channel handle):
            <li>
                <code><a
                        href="https://www.youtube.com/c/CoryWongMusic">https://www.youtube.com/c/CoryWongMusic</a></code>
                <ol>
                    <li><code><a href="http://localhost:5446/c/CoryWongMusic">http://localhost:5446/c/CoryWongMusic</a></code></li>
                </ol>
            </li>
            <li>
                <code><a href="https://youtube.com/c/@AdamNeely">https://youtube.com/c/@AdamNeely</a></code>
                <ol>
                    <li><code><a href="http://localhost:5446/c/@AdamNeely">http://localhost:5446/c/@AdamNeely</a></code></li>
                </ol>
            </li>
            Playlist (playlist id):
            <li>
                <code><a href="https://www.youtube.com/playlist?list=PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt">https://www.youtube.com/playlist?list=PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt</a></code>
                <ol>
                    <li>
                        <code><a href="http://localhost:5446/p/PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt">http://localhost:5446/p/PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt</a></code>
                    </li>
                </ol>
            </li>
            <li>
                <code><a href="https://www.youtube.com/playlist?list=PLz4scdcuqnN2oK16dHadxF1JTAaW1snBu">https://www.youtube.com/playlist?list=PLz4scdcuqnN2oK16dHadxF1JTAaW1snBu</a></code>
                <ol>
                    <li>
                        <code><a href="http://localhost:5446/p/PLz4scdcuqnN2oK16dHadxF1JTAaW1snBu">http://localhost:5446/p/PLz4scdcuqnN2oK16dHadxF1JTAaW1snBu</a></code>
                    </li>
                </ol>
            </li>
            User (channel id):
            <li><code><a href="https://www.youtube.com/channel/UCj1VqrHhDte54oLgPG4xpuQ">https://www.youtube.com/channel/UCj1VqrHhDte54oLgPG4xpuQ</a></code>
                <ol>
                    <li>
                        <code><a
                                href="http://localhost:5446/u/UCj1VqrHhDte54oLgPG4xpuQ">http://localhost:5446/u/UCj1VqrHhDte54oLgPG4xpuQ</a></code>
                    </li>
                </ol>
            </li>
            <li><code><a href="https://www.youtube.com/channel/UCnLozCO8w7uJODg8_iAGaVw">https://www.youtube.com/channel/UCnLozCO8w7uJODg8_iAGaVw</a></code>
                <ol>
                    <li>
                        <code><a
                                href="http://localhost:5446/u/UCnLozCO8w7uJODg8_iAGaVw">http://localhost:5446/u/UCnLozCO8w7uJODg8_iAGaVw</a></code>
                    </li>
                </ol>
            </li>
        </ul>
    </li>
    <li>
        <p>Add this RSS feed to your podcatcher of choice. I would recommend creating a podcast playlist on your
            YouTube account and saving wanted videos in that playlist if you do not want to have access to an
            entire channel or want to mix different videos from different channels.</p>
    </li>
    <li>
        <p>If you want to download the audio for a single video, you can use the <b>download (dl)</b> routes. Examples:
        </p>
        <ul>
            <li>
                <code><a
                        href="https://www.youtube.com/watch?v=5LyUgE4XPuU">https://www.youtube.com/watch?v=5LyUgE4XPuU</a></code>
                <ol>
                    <li>
                        <code><a href="http://localhost:5446/dl/5LyUgE4XPuU.m4a">http://localhost:5446/dl/5LyUgE4XPuU.m4a</a></code>
                    </li>
                </ol>
            </li>
            <li>
                <code><a
                        href="https://www.youtube.com/watch?v=Xo3xqm-AtqE">https://www.youtube.com/watch?v=Xo3xqm-AtqE</a></code>
                <ol>
                    <li>
                        <code><a href="http://localhost:5446/dl/Xo3xqm-AtqE.m4a">http://localhost:5446/dl/Xo3xqm-AtqE.m4a</a></code>
                    </li>
                </ol>
            </li>
        </ul>
    </li>
</ul>

## Hosting

### Pre-reqs

You'll need a YouTube api key. Information on how to get one can be found [here](https://developers.google.com/youtube/v3/getting-started).

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

### Deployment

There is a repo that contains an edge server image and a docker compose file that can be used to deploy the app.
Information on how to use it can be found [here](https://github.com/jaredkoontz/yt_feed_deploy). This is the recommended
way to deploy the app and how I run it.
