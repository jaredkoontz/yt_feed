#!/bin/bash

# this is a template script for deploying.
# if you want to make changes to this, you could `git update-index --assume-unchanged <filename>`

YT_KEY=""
DOM=""

set -x

docker pull ghcr.io/jaredkoontz/yt_feed:main

docker stop "$(docker ps -a -q)"

docker run\
 -e YOUTUBE_API_KEY="$YT_KEY"\
 -e DOMAIN="$DOM"\
 -p 80:80\
 --rm -d\
 --memory=512m\
 --memory-swap=512m\
 ghcr.io/jaredkoontz/yt_feed:main
