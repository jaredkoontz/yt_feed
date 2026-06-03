# inspired by https://github.com/astral-sh/uv-docker-example/blob/6473a50c02f9c36dda8c29cf3e0b6fd84839d353/standalone.Dockerfile
# First, build the application in the `/yt_feed` directory
FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Configure the Python directory so it is consistent
ENV UV_PYTHON_INSTALL_DIR=/python

# Only use the managed Python version
ENV UV_PYTHON_PREFERENCE=only-managed

# Install Python before the project for caching
RUN uv python install 3.13

WORKDIR /app

COPY uv.lock /app
COPY pyproject.toml /app
COPY README.md /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=/app/uv.lock \
    --mount=type=bind,source=pyproject.toml,target=/app/pyproject.toml \
    uv sync --locked --no-install-project --no-dev

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=yt_feed,target=/app/yt_feed \
    uv build --wheel --out-dir /tmp/wheels

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /app/.venv/bin/python --no-deps /tmp/wheels/*.whl

# Then, use a final image without uv
FROM debian:bookworm-slim

# Copy the Python version
COPY --from=builder /python /python

# Copy the virtual environment containing the application wheel
COPY --from=builder /app/.venv /app/.venv

WORKDIR /app

# get our dependencies for ytp-dl
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
      ca-certificates \
      ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# ytp-dl also requires a js runtime
COPY --from=denoland/deno:bin-2.6.7 /deno /usr/local/bin/deno

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# we could copy an .env file if we have one.
COPY .env* /app/.env

CMD ["gunicorn", "--conf", "python:yt_feed.conf.gunicorn_conf", "--bind", "0.0.0.0:80", "yt_feed.web_app:yt_feed_app"]
