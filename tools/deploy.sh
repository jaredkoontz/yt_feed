#!/bin/bash

# this is a template script for deploying.
# if you want to make changes to this, you could `git update-index --assume-unchanged <filename>`

YT_KEY=""
DOM=""

IMAGE="ghcr.io/jaredkoontz/yt_feed:main"
NETWORK="yt_feed_net"
APP_CONTAINER="yt_feed_app"
EDGE_CONTAINER="yt_feed_edge"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

set -x

docker pull "$IMAGE"
docker pull nginx:1.27-alpine

docker network create "$NETWORK" || true

docker stop "$EDGE_CONTAINER" "$APP_CONTAINER" || true
docker rm "$EDGE_CONTAINER" "$APP_CONTAINER" || true

docker run \
 --name "$APP_CONTAINER" \
 --network "$NETWORK" \
 -e YOUTUBE_API_KEY="$YT_KEY"\
 -e DOMAIN="$DOM"\
 --rm -d\
 --ulimit nofile=65536:65536\
 --memory=512m\
 --memory-swap=512m\
 "$IMAGE" \
 gunicorn --conf app/yt_feed/conf/gunicorn_conf.py --bind 0.0.0.0:8000 yt_feed.web_app:yt_feed_app

docker run \
 --name "$EDGE_CONTAINER" \
 --network "$NETWORK" \
 -p 80:80 \
 --rm -d \
 --ulimit nofile=65536:65536 \
 -v "$SCRIPT_DIR/nginx.conf:/etc/nginx/nginx.conf:ro" \
 nginx:1.27-alpine
