FROM python:3.10
#could do -slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates ffmpeg

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"

COPY ./uv.lock /code/uv.lock
COPY ./pyproject.toml /code/pyproject.toml

WORKDIR /code

RUN uv venv
RUN uv sync --all-extras --dev

COPY ./yt_feed /code/yt_feed
COPY ./yt_feed.ini /code/yt_feed.ini

CMD ["uv", "run", "gunicorn", "--conf", "yt_feed/conf/gunicorn_conf.py", "--bind", "0.0.0.0:80", "yt_feed.web_app:app"]
