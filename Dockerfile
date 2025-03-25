FROM python:3.10
#could do -slim-bookworm

# get uv
# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates ffmpeg

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /code

COPY ./uv.lock /code/uv.lock
COPY ./pyproject.toml /code/pyproject.toml

RUN uv venv
RUN uv sync --all-extras --dev

COPY ./yt_feed /code/yt_feed

CMD ["uv", "run", "python", "-m", "yt_feed.runner"]

#CMD ["gunicorn", "--conf", "yt_feed/conf/gunicorn_conf.py", "--bind", "0.0.0.0:80", "app.main:app"]
