# yt_feed

Create a working RSS feed (for your podcatcher) to turn a YouTube channel into a podcast.

[![yt_feed](https://github.com/jaredkoontz/yt_feed/actions/workflows/python-app.yml/badge.svg)](https://github.com/jaredkoontz/yt_feed/actions/workflows/python-app.yml)
[![Docker](https://github.com/jaredkoontz/yt_feed/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/jaredkoontz/yt_feed/actions/workflows/docker-publish.yml)

## User Instructions

<p>Convert any YouTube channel or playlist to a podcast. Defaults to audio, but can also do video. This tool will
    create a feed for your podcatcher, and then handle the streaming of the audio when your podcatcher requests
    it.</p>
<h2>Usage</h2>
<ol>
    <li>
        <p>LOREM IPSUM</p>
        <ul>
            <li><code><a href="https://youtube.com/c/@stuffmadehere">https://youtube.com/c/@stuffmadehere</a></code>
            </li>
            <ol>
                <li>/c/@stuffmadehere</li>
            </ol>
            <li><code><a href="https://youtube.com/c/stuffmadehere">https://youtube.com/c/stuffmadehere</a></code>
            </li>
            <ol>
                <li>/c/stuffmadehere</li>
            </ol>
            <li><code><a href="https://www.youtube.com/watch?v=KMd5czoOW-Q&list=PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt">https://www.youtube.com/watch?v=KMd5czoOW-Q&list=PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt</a></code>
            </li>
            <ol>
                <li>/p/PLq5Wss5r1Cvtfc3KcM-34zIQE6hQz-DJt/v</li>
            </ol>
            <li><code><a href="https://www.youtube.com/channel/UCj1VqrHhDte54oLgPG4xpuQ">https://www.youtube.com/channel/UCj1VqrHhDte54oLgPG4xpuQ</a></code>
            </li>
            <ol>
                <li>/u/UCj1VqrHhDte54oLgPG4xpuQ</li>
            </ol>
        </ul>
    </li>

    <li>
        <p>audio by default</p>
        <ul>
            <li><code>https:///c/beardmeatsfood/v</code></li>
        </ul>
        <p>This works for all urls described, simply just append a `/v`</p>
    </li>

    <li>
        <p>Hit subscribe. You&#39;re all set. You can now download and refresh episodes, just like with any other
            podcast.</p>
    </li>
</ol>

## Dev Instructions
